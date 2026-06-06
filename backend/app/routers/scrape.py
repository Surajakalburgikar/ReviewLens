"""
FastAPI router for URL-based review scraping.

Exposes: GET /api/v1/scrape?url=https://...

The frontend calls this FIRST with a URL.
If scraping succeeds, the extracted text is returned to the frontend.
The frontend then displays it in the textarea and lets the user
click "Analyze" — which calls the existing /analyze endpoint normally.

This two-step design means:
  1. The scrape endpoint is fast and lightweight (just fetches text)
  2. The analyze endpoint stays unchanged — single responsibility
  3. Users can edit the scraped text before analyzing it
"""
import logging
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from app.scraper.scraper import scrape_reviews_from_url

logger = logging.getLogger(__name__)
router = APIRouter()


class ScrapeResponse(BaseModel):
    """Response envelope for the scrape endpoint."""
    text: str                 # extracted review text (empty string on failure)
    source: str               # which scraper was used: google_play | app_store | generic
    count: int                # number of reviews/paragraphs extracted
    error: Optional[str]      # None on success, error message on failure


@router.get(
    "/scrape",
    response_model=ScrapeResponse,
    summary="Extract reviews from a URL",
    description=(
        "Fetches and extracts review text from a given URL. "
        "Supports Google Play Store app pages, Apple App Store app pages, "
        "and generic web review pages. "
        "Returns the extracted text for display and editing before analysis."
    ),
)
async def scrape_url(
    url: str = Query(
        ...,
        description="The URL to scrape reviews from.",
        min_length=10,
        max_length=2000,
    )
) -> ScrapeResponse:
    """
    Scrapes review text from the provided URL.

    The frontend shows the extracted text in the textarea before analysis.
    This allows users to verify and edit the text if needed.
    """
    # Basic URL validation — must start with http
    if not url.startswith(("http://", "https://")):
        return ScrapeResponse(
            text="",
            source="unknown",
            count=0,
            error="URL must start with http:// or https://"
        )

    logger.info(f"Scrape request received for URL: {url[:80]}...")

    result = await scrape_reviews_from_url(url)

    return ScrapeResponse(
        text=result["text"],
        source=result["source"],
        count=result["count"],
        error=result["error"],
    )
