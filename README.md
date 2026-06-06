# ReviewLens — Explainable AI Sentiment & Summarizer

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React_19-20232A?style=flat&logo=react)](https://react.dev)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql)](https://www.postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Live Demo:** https://review-lens-mocha.vercel.app
**Backend API:** https://reviewlens-n7nt.onrender.com

ReviewLens is a production-ready NLP web application that extracts, summarizes, and classifies product reviews. It uses a **hybrid Logistic Regression + TextBlob sentiment model** trained inline at startup, **Explainable AI (XAI)** to show which words drove each prediction, **extractive text summarization** using frequency-based sentence scoring, and a **URL-based review scraper** supporting Google Play Store, Apple App Store, and generic web pages.

---

## 🏗️ System Architecture

```
Browser Client
     │
     ├─── Paste Text ──────────────────────────────────────────┐
     │                                                          │
     └─── From URL ──► GET /api/v1/scrape?url=...              │
                           │                                    │
                    Scraper (Google Play /                      │
                    App Store / Generic)                        │
                           │                                    │
                    Returns extracted text ◄─────── User edits │
                           │                                    │
                           └────────────────────────────────────┘
                                        │
                               POST /api/v1/analyze
                                        │
                              ┌─────────▼──────────┐
                              │   FastAPI Backend   │
                              │   (Render)          │
                              └─────────┬──────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
            Summarizer            Predictor              Database
         (NLTK frequency      (TF-IDF + LR +         (Supabase
          sentence scoring)    TextBlob hybrid)        PostgreSQL)
                    │                   │
            summary, keywords    sentiment, confidence,
            word_count           XAI influential words
                    │                   │
                    └───────────────────┘
                                │
                    Returns { data, error: null }
                                │
                    React renders Result Card
```

---

## ✨ Features

- **Dual Input Modes** — paste review text directly OR fetch from a URL
- **URL Scraping** — supports Google Play Store (80 reviews), Apple App Store (RSS API), and generic web pages
- **Hybrid Sentiment Model** — Logistic Regression (TF-IDF) + TextBlob polarity blend for improved accuracy
- **Explainable AI (XAI)** — shows the top 5 words that most influenced each prediction with normalized scores
- **Extractive Summarization** — frequency-based sentence scoring with deduplication, returns top 2-3 sentences
- **Keyword Extraction** — top 5 keywords by frequency after stopword removal
- **Text Metrics** — word count, sentence count, reading time
- **Session History** — all analyses stored per anonymous session UUID (no login required)
- **Confidence Score** — visual bar chart showing prediction certainty (0–100%)

---

## 🛠️ Technology Stack

| Component | Technology | Role |
|:----------|:-----------|:-----|
| **Frontend** | React 19 + Vite | SPA with modern hooks and tab-based UI |
| **Charts** | Recharts | Confidence score bar visualization |
| **Icons** | Lucide React | Clean SVG icon set |
| **HTTP Client** | Axios | API requests with 60s timeout for cold starts |
| **Backend** | FastAPI (Python) | Async REST API with OpenAPI docs |
| **ML Pipeline** | scikit-learn | TF-IDF vectorizer + Logistic Regression |
| **Sentiment Lexicon** | TextBlob | Hybrid signal for wider vocabulary coverage |
| **NLP** | NLTK | Sentence tokenization, stopwords, summarization |
| **Scraping** | httpx + BeautifulSoup + google-play-scraper | URL-based review extraction |
| **ORM** | SQLAlchemy 2.0 (async) | Async database session management |
| **Database** | PostgreSQL (Supabase) | Persistent analysis history storage |
| **Migrations** | Alembic | Version-controlled schema management |
| **Backend Host** | Render (free tier) | Python 3.11 runtime |
| **Frontend Host** | Vercel | Static SPA with SPA rewrites |

---

## 📁 Project Structure

```
ReviewLens/
├── backend/
│   ├── app/
│   │   ├── ml/
│   │   │   ├── trainer.py        # Trains TF-IDF + LR pipeline at startup (120 samples)
│   │   │   ├── predictor.py      # Hybrid sentiment prediction + XAI word attribution
│   │   │   └── summarizer.py     # Extractive summarization + keyword extraction
│   │   ├── models/
│   │   │   └── analysis.py       # SQLAlchemy ORM model (cross-DB UUID type)
│   │   ├── routers/
│   │   │   ├── analyze.py        # POST /api/v1/analyze
│   │   │   ├── history.py        # GET /api/v1/history/{session_id}
│   │   │   └── scrape.py         # GET /api/v1/scrape?url=...
│   │   ├── schemas/
│   │   │   └── analysis.py       # Pydantic request/response schemas
│   │   ├── scraper/
│   │   │   └── scraper.py        # Google Play / App Store / Generic scrapers
│   │   ├── config.py             # Pydantic BaseSettings (env vars)
│   │   ├── database.py           # Async SQLAlchemy engine + session
│   │   └── main.py               # FastAPI app factory, CORS, lifespan
│   ├── alembic/                  # Database migrations
│   ├── .env.example              # Required environment variables
│   ├── .python-version           # Pins Python 3.11.9 for Render
│   └── requirements.txt          # All pinned dependencies
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── axios.js          # Axios instance (60s timeout, withCredentials: false)
│   │   ├── components/
│   │   │   ├── AnalysisForm.jsx  # Two-tab form: Paste Text + From URL
│   │   │   └── ResultCard.jsx    # Sentiment badge, confidence bar, XAI words
│   │   ├── pages/
│   │   │   ├── Home.jsx          # Main analysis page
│   │   │   └── History.jsx       # Past analyses for current session
│   │   ├── utils/
│   │   │   └── session.js        # localStorage UUID session management
│   │   └── index.css             # Dark theme with CSS variables
│   ├── vercel.json               # SPA rewrite rules
│   └── package.json
├── .gitignore
└── README.md
```

---

## 🔌 API Reference

### POST `/api/v1/analyze`
Analyze a review text and return sentiment, summary, keywords, and XAI.

**Request:**
```json
{
  "text": "The product quality is amazing, exceeded all expectations.",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "sentiment": "Positive",
    "confidence": 0.87,
    "summary": "The product quality is amazing...",
    "keywords": ["quality", "amazing", "product", "exceeded", "expectations"],
    "top_influential_words": [
      {"word": "amazing", "score": 1.0},
      {"word": "exceeded", "score": 0.72}
    ],
    "word_count": 10,
    "sentence_count": 1,
    "reading_time_seconds": 3,
    "created_at": "2026-06-06T12:00:00Z"
  },
  "error": null
}
```

---

### GET `/api/v1/scrape?url=`
Fetch and extract review text from a URL.

**Supported sources:**
| Source | Example URL | Method |
|--------|------------|--------|
| Google Play Store | `play.google.com/store/apps/details?id=com.whatsapp` | google-play-scraper library |
| Apple App Store | `apps.apple.com/in/app/name/id123456789` | Apple public RSS API |
| Generic web pages | Any URL with `<p>` tag content | httpx + BeautifulSoup |
| ❌ Amazon / Flipkart | — | Blocked by bot detection |

**Response:**
```json
{
  "text": "Combined extracted review text...",
  "source": "google_play",
  "count": 80,
  "error": null
}
```

---

### GET `/api/v1/history/{session_id}`
Returns the last 10 analyses for an anonymous session.

### GET `/api/v1/history/{session_id}/{analysis_id}`
Returns a single specific analysis by ID.

### GET `/`
Health check — returns `{"status": "online"}`.

---

## ⚙️ Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate — Windows:
.\venv\Scripts\activate
# Activate — Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and fill environment variables
cp .env.example .env
# Edit .env — set DATABASE_URL (or leave blank for SQLite)

# Run migrations (SQLite auto-created if no DATABASE_URL set)
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`

NLTK resources (`punkt`, `punkt_tab`, `stopwords`) and the ML model are downloaded and trained automatically at startup — no manual setup needed.

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## 🚀 Deployment

### Backend — Render (Free Tier)

| Field | Value |
|-------|-------|
| **Runtime** | Python 3 |
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `cd /opt/render/project/src/backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers` |
| **Python Version** | Pinned via `backend/.python-version` → `3.11.9` |

**Required Environment Variables in Render:**

| Key | Value |
|-----|-------|
| `APP_ENV` | `production` |
| `DATABASE_URL` | Supabase Session Pooler URL with `?ssl=require` |
| `ALLOWED_ORIGINS` | Your Vercel URL e.g. `https://review-lens-mocha.vercel.app` |
| `API_VERSION` | `v1` |

> **Important:** Use the Supabase **Session Pooler** URL (port 5432, `aws-x-region.pooler.supabase.com`) — not the Direct Connection. Direct Connection is IPv6 only and unreachable from Render free tier.

### Frontend — Vercel (Free Tier)

| Field | Value |
|-------|-------|
| **Framework** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

**Required Environment Variable in Vercel:**

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://your-render-app.onrender.com` (no trailing slash) |

`vercel.json` handles SPA routing automatically — all routes serve `index.html`.

### Database — Supabase (Free Tier)

1. Create project at [supabase.com](https://supabase.com)
2. Go to **Connect → Session Pooler** → copy URI
3. Replace `postgresql://` with `postgresql+asyncpg://`
4. Append `?ssl=require`
5. Set as `DATABASE_URL` in Render

Alembic runs `upgrade head` automatically on every deploy — no manual migration needed.

---

## 🧠 How the ML Pipeline Works

### Sentiment Prediction (Hybrid Model)

The model uses two signals blended together:

**Signal 1 — TF-IDF + Logistic Regression (40% weight)**
- Trained inline at startup on 120 labeled reviews (60 positive, 60 negative)
- Vocabulary: 1000 unigrams and bigrams, sublinear TF normalization
- Trains in under 1 second — no pickle files, no external dependencies
- Provides XAI feature importances via `coef_` attribute

**Signal 2 — TextBlob Polarity Lexicon (60% weight)**
- Pre-trained on thousands of reviews — handles unseen vocabulary
- Maps polarity score (-1.0 to +1.0) to confidence percentage
- Acts as tiebreaker when LR is uncertain

**Blending logic:**
- If both signals agree → blend confidences, high certainty
- If they disagree → TextBlob wins as tiebreaker, lower confidence
- If blended confidence < 58% → classified as **Neutral**

### Explainable AI (XAI)

```
Influence Score = TF-IDF weight × Logistic Regression coefficient
```

For each word in the input text that exists in the TF-IDF vocabulary:
- Positive coefficient + positive TF-IDF weight → pushed prediction toward Positive
- Negative coefficient → pushed prediction toward Negative
- Top 5 words by influence are returned with normalized scores (0.0–1.0)

### Extractive Summarization

1. Tokenize text into sentences (NLTK `sent_tokenize`)
2. Build word frequency table (after stopword removal)
3. Score each sentence by summing frequencies of its words
4. Select sentences scoring > 1.2× average score (threshold tuned)
5. Cap at 3 sentences, sort back to original order
6. Deduplicate sentences with >70% overlap

---

## 💡 What This Project Demonstrates

| Skill | Implementation |
|-------|---------------|
| Async Python | FastAPI + async SQLAlchemy 2.0 + asyncpg throughout |
| ML serving as API | Logistic Regression pipeline trained at startup, served via REST |
| Explainable AI | TF-IDF × coefficient attribution scores per word |
| Layered architecture | Router → Service (ML) → Repository → Model |
| Web scraping | Three-source scraper with graceful fallbacks |
| Cross-DB compatibility | Custom `UUIDType` works on both SQLite (dev) and PostgreSQL (prod) |
| Async database | SQLAlchemy async sessions with Alembic migrations |
| Anonymous sessions | UUID stored in `localStorage` — no login required |
| Production deployment | Render + Vercel + Supabase + environment-aware config |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
