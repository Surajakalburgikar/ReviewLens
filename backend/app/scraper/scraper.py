"""
URL-based review scraper for ReviewLens.

Supports 3 reliable sources that actually work — unlike Amazon/Flipkart:

  1. Google Play Store app reviews
     URL format: https://play.google.com/store/apps/details?id=com.example.app
     Method: Uses google-play-scraper Python library (no browser, no blocking)

  2. Apple App Store reviews (via Apple's public RSS API)
     URL format: https://apps.apple.com/in/app/app-name/id123456789
     Method: Calls Apple's official iTunes RSS JSON endpoint — free, no key needed

  3. Generic web article / review page (fallback)
     Method: httpx + BeautifulSoup — extracts all <p> tags and filters by length
     Works on: review blogs, Reddit, news articles, Trustpilot listings, etc.
     Does NOT work on: Amazon, Flipkart (anti-bot), SPAs requiring JavaScript

Why these 3?
- Google Play: 1 billion+ app reviews, no scraping blocks — official library
- App Store: Apple provides an official public RSS/JSON feed — zero rate limiting
- Generic fallback: handles the vast majority of real-world review pages

Returns:
  dict with keys:
    "text"   — the combined review text (str)
    "source" — which scraper was used (str)
    "count"  — number of reviews extracted (int)
    "error"  — None on success, error message string on failure
"""

import re
import logging
from typing import Optional
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


# ── Helper: detect URL type ────────────────────────────────────────────────────

def _detect_source(url: str) -> str:
    """Detects which scraper to use based on the URL domain."""
    url_lower = url.lower()
    if "play.google.com" in url_lower:
        return "google_play"
    if "apps.apple.com" in url_lower or "itunes.apple.com" in url_lower:
        return "app_store"
    return "generic"


# ── Scraper 1: Google Play Store ──────────────────────────────────────────────

def _extract_app_id_from_play_url(url: str) -> Optional[str]:
    """
    Extracts the app package ID from a Google Play URL.
    Example: https://play.google.com/store/apps/details?id=com.whatsapp
    Returns: "com.whatsapp"
    """
    match = re.search(r"[?&]id=([a-zA-Z0-9._]+)", url)
    return match.group(1) if match else None


def scrape_google_play(url: str) -> dict:
    """
    Fetches up to 100 reviews from Google Play Store using
    the google-play-scraper library.

    Why this works: google-play-scraper calls Google's internal API endpoints
    directly — no HTML parsing, no browser automation, no rate limiting issues.

    Args:
        url: Google Play Store app URL

    Returns:
        dict with text, source, count, error
    """
    try:
        # Import here so missing package gives a clear error only when used
        from google_play_scraper import reviews, Sort  # type: ignore
    except ImportError:
        return {
            "text": "",
            "source": "google_play",
            "count": 0,
            "error": "google-play-scraper package not installed. Run: pip install google-play-scraper"
        }

    app_id = _extract_app_id_from_play_url(url)
    if not app_id:
        return {
            "text": "",
            "source": "google_play",
            "count": 0,
            "error": "Could not extract app ID from the Google Play URL. "
                     "Make sure the URL contains ?id=com.example.app"
        }

    try:
        logger.info(f"Fetching Google Play reviews for app: {app_id}")

        # Fetch 80 most relevant reviews in English
        result, _ = reviews(
            app_id,
            lang="en",
            country="in",       # India — change to 'us' for US reviews
            sort=Sort.MOST_RELEVANT,
            count=80,
        )

        if not result:
            return {
                "text": "",
                "source": "google_play",
                "count": 0,
                "error": "No English reviews found for this app on Google Play."
            }

        # Combine all review text bodies into one string
        # Each review has a 'content' field with the review text
        review_texts = [r["content"] for r in result if r.get("content", "").strip()]

        combined = " ".join(review_texts)

        logger.info(f"Extracted {len(review_texts)} Google Play reviews ({len(combined)} chars)")
        return {
            "text": combined,
            "source": "google_play",
            "count": len(review_texts),
            "error": None,
        }

    except Exception as e:
        logger.error(f"Google Play scraper error: {e}")
        return {
            "text": "",
            "source": "google_play",
            "count": 0,
            "error": f"Failed to fetch Google Play reviews: {str(e)}"
        }


# ── Scraper 2: Apple App Store ─────────────────────────────────────────────────

def _extract_app_id_from_apple_url(url: str) -> Optional[str]:
    """
    Extracts the numeric app ID from an App Store URL.
    Example: https://apps.apple.com/in/app/instagram/id389801252
    Returns: "389801252"
    """
    match = re.search(r"/id(\d+)", url)
    return match.group(1) if match else None


async def scrape_app_store(url: str) -> dict:
    """
    Fetches reviews from Apple App Store using Apple's official public RSS API.

    Apple provides a free, rate-limit-free JSON RSS feed for every app:
    https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/json

    No scraping, no browser, no API key needed — this is official Apple data.

    Args:
        url: Apple App Store app URL

    Returns:
        dict with text, source, count, error
    """
    app_id = _extract_app_id_from_apple_url(url)
    if not app_id:
        return {
            "text": "",
            "source": "app_store",
            "count": 0,
            "error": "Could not extract app ID from the App Store URL. "
                     "Make sure the URL contains /id followed by numbers."
        }

    # Try multiple country feeds to maximize review count
    # Apple's RSS only returns ~50 reviews per country feed
    countries = ["in", "us", "gb"]
    all_review_texts = []

    async with httpx.AsyncClient(timeout=15.0) as client:
        for country in countries:
            rss_url = (
                f"https://itunes.apple.com/{country}/rss/customerreviews"
                f"/id={app_id}/sortBy=mostRecent/json"
            )
            try:
                logger.info(f"Fetching App Store RSS feed: {rss_url}")
                resp = await client.get(rss_url)

                if resp.status_code != 200:
                    continue

                data = resp.json()

                # Apple RSS JSON structure: feed.entry is a list of reviews
                # First entry is the app metadata, skip it
                entries = data.get("feed", {}).get("entry", [])
                if not entries:
                    continue

                # Skip first entry (it's app info, not a review)
                for entry in entries[1:]:
                    # Review text is in entry["content"]["label"]
                    content = entry.get("content", {})
                    review_text = content.get("label", "").strip()
                    if review_text and len(review_text) > 10:
                        all_review_texts.append(review_text)

            except Exception as e:
                logger.warning(f"App Store RSS fetch failed for country {country}: {e}")
                continue

    if not all_review_texts:
        return {
            "text": "",
            "source": "app_store",
            "count": 0,
            "error": "No reviews found for this app on the App Store. "
                     "The app may not have English reviews or may not be publicly listed."
        }

    # Deduplicate (same review can appear in multiple country feeds)
    seen = set()
    unique_reviews = []
    for r in all_review_texts:
        if r not in seen:
            seen.add(r)
            unique_reviews.append(r)

    combined = " ".join(unique_reviews)
    logger.info(f"Extracted {len(unique_reviews)} App Store reviews ({len(combined)} chars)")

    return {
        "text": combined,
        "source": "app_store",
        "count": len(unique_reviews),
        "error": None,
    }


# ── Scraper 3: Generic Web Page (fallback) ─────────────────────────────────────

async def scrape_generic(url: str) -> dict:
    """
    Generic HTML scraper for review pages, blogs, and articles.

    Strategy:
    1. Fetch page HTML with httpx (fast, async, no browser needed)
    2. Parse with BeautifulSoup
    3. Extract all <p> tags
    4. Filter out navigation/footer noise (keep paragraphs > 40 characters)
    5. Combine into single text block

    Works well for: Trustpilot, G2, Capterra, review blogs, Reddit posts
    Does NOT work for: Amazon (bot detection), Flipkart (bot detection),
                       React/Vue SPAs (content rendered by JavaScript)

    Args:
        url: Any web URL

    Returns:
        dict with text, source, count, error
    """
    headers = {
        # Pretend to be a regular Chrome browser
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            logger.info(f"Fetching generic URL: {url}")
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return {
                "text": "",
                "source": "generic",
                "count": 0,
                "error": f"Page returned HTTP {response.status_code}. "
                         f"The website may be blocking automated requests. "
                         f"Try copying and pasting the review text directly."
            }

        # Parse HTML
        soup = BeautifulSoup(response.content, "lxml")

        # Remove script, style, nav, header, footer — noise elements
        for tag in soup(["script", "style", "nav", "header", "footer",
                          "aside", "noscript", "iframe"]):
            tag.decompose()

        # Extract all paragraph text
        paragraphs = soup.find_all("p")
        extracted = []
        for p in paragraphs:
            text = p.get_text(separator=" ", strip=True)
            # Keep only paragraphs that are long enough to be real review content
            # Short ones are usually navigation labels, copyright notices, etc.
            if len(text) > 40:
                extracted.append(text)

        if not extracted:
            return {
                "text": "",
                "source": "generic",
                "count": 0,
                "error": "Could not extract any review text from this URL. "
                         "The page may use JavaScript to render content (SPA), "
                         "or may not contain paragraph text. "
                         "Please copy and paste the review text directly."
            }

        combined = " ".join(extracted)

        # Safety limit — cap at 5000 chars to match our analysis endpoint limit
        if len(combined) > 5000:
            combined = combined[:5000]

        logger.info(f"Generic scraper extracted {len(extracted)} paragraphs ({len(combined)} chars)")
        return {
            "text": combined,
            "source": "generic",
            "count": len(extracted),
            "error": None,
        }

    except httpx.TimeoutException:
        return {
            "text": "",
            "source": "generic",
            "count": 0,
            "error": "Request timed out after 15 seconds. The website may be slow or blocking requests."
        }
    except Exception as e:
        logger.error(f"Generic scraper error for {url}: {e}")
        return {
            "text": "",
            "source": "generic",
            "count": 0,
            "error": f"Failed to fetch the URL: {str(e)}"
        }


# ── Main entry point ───────────────────────────────────────────────────────────

async def scrape_reviews_from_url(url: str) -> dict:
    """
    Main dispatcher — detects URL type and calls the right scraper.

    Args:
        url: Any URL (Google Play, App Store, or generic web page)

    Returns:
        dict with keys: text, source, count, error
    """
    source = _detect_source(url)
    logger.info(f"URL '{url}' detected as source: {source}")

    if source == "google_play":
        # google-play-scraper is synchronous — run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, scrape_google_play, url)

    elif source == "app_store":
        return await scrape_app_store(url)

    else:
        return await scrape_generic(url)
