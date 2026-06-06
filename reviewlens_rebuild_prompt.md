# ReviewLens Rebuild Prompt for Claude Code
# Paste this ENTIRE prompt into Claude Code / Claude Sonnet

---

## CONTEXT — WHAT EXISTS AND WHAT IS WRONG

I have an existing project called ReviewLens — a sentiment analysis and text
summarization app. The current version has major problems I need you to fix
while rebuilding it to a professional but fresher-appropriate level:

CURRENT PROBLEMS:
1. Built with Django (monolithic, hard to deploy, slow, overkill for this)
2. global variables used for state (count, strg, flag) — terrible practice
3. All logic crammed into views.py — no separation whatsoever
4. Binary .sav model file committed to repo — bad practice, slow cold start
5. Scraping Amazon/Flipkart is blocked 95% of the time — broken feature
6. No API — just Django HTML templates, cannot be tested or extended
7. scikit-learn version pinning is fragile — breaks on different machines
8. No comments, no docstrings anywhere
9. Not deployable on Render (binary model file, Django complexity)
10. TF-IDF fitted on a separate CSV at runtime — fragile and slow

---

## WHAT TO BUILD — THE UPGRADED VERSION

Build "ReviewLens" — a Sentiment Analysis & Text Summarization API with a 
clean React frontend. Deployed and live. Professional but fresher-appropriate.

### Core Concept (same as before, but done RIGHT)
User pastes ANY product review text (Amazon, Flipkart, any review text)
→ App returns:
  1. Sentiment: Positive / Negative / Neutral with a confidence percentage
  2. Extractive Summary: 2-3 most important sentences from the text
  3. Key Themes: top 5 keywords extracted from the review
  4. Word count, sentence count, reading time estimate

### The One Impressive Technical Thing
"Model explainability — after predicting sentiment, the API returns the top 5 
words that most influenced the prediction using feature importances from the 
TF-IDF + Logistic Regression pipeline. This is called XAI (Explainable AI)."

---

## TECH STACK — FREE TIERS ONLY, NO CREDIT CARD

Backend:
- FastAPI (Python) — NOT Django
- scikit-learn — Logistic Regression (train inline at startup, no .sav file)
- NLTK — for tokenization and summarization
- Supabase PostgreSQL — store analysis history (no login needed, use session UUID)
- Render — for deployment

Frontend:
- React 19 + Vite
- No external UI library — vanilla CSS with CSS variables (dark theme)
- Recharts — for the confidence score bar chart
- Vercel — for deployment

NO: No login/auth (not needed for this project)
NO: No web scraping (broken, unreliable — user pastes text directly)
NO: Binary .sav model files committed to repo
NO: Global variables
NO: Everything in one file

---

## PROJECT STRUCTURE TO BUILD

```
reviewlens/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app factory, lifespan, middleware
│   │   ├── config.py            # Pydantic BaseSettings, env vars
│   │   ├── database.py          # Async SQLAlchemy setup
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── analysis.py      # Analysis ORM model (stores history)
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── analysis.py      # Pydantic request/response schemas
│   │   ├── ml/
│   │   │   ├── __init__.py
│   │   │   ├── trainer.py       # Trains model at startup using sample data
│   │   │   ├── predictor.py     # Sentiment prediction + explainability
│   │   │   └── summarizer.py    # Extractive summarization + keywords
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── analyze.py       # POST /api/v1/analyze endpoint
│   │       └── history.py       # GET /api/v1/history/{session_id}
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── .env.example
│   └── .python-version          # 3.11.9
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api/
│   │   │   └── axios.js         # Axios instance
│   │   ├── pages/
│   │   │   ├── Home.jsx         # Main analysis page
│   │   │   └── History.jsx      # Past analyses for this session
│   │   ├── components/
│   │   │   ├── AnalysisForm.jsx # Text input form
│   │   │   ├── ResultCard.jsx   # Shows sentiment + summary + keywords
│   │   │   ├── SentimentBar.jsx # Recharts confidence bar
│   │   │   └── KeywordChip.jsx  # Styled keyword tag
│   │   ├── utils/
│   │   │   └── session.js       # Generate/persist UUID in localStorage
│   │   └── index.css            # CSS variables dark theme
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── vercel.json
├── .gitignore
└── README.md
```

---

## DETAILED REQUIREMENTS FOR EACH FILE

### backend/app/ml/trainer.py
"""
Train a Logistic Regression + TF-IDF pipeline AT STARTUP — no .sav files.
Use a hardcoded mini dataset of 60 labeled reviews (30 positive, 30 negative)
directly in this file as a Python list. This avoids:
- Fragile CSV file dependency
- Binary pickle files in the repo
- Version compatibility issues

The pipeline:
  TfidfVectorizer(max_features=500, ngram_range=(1,2)) → LogisticRegression()

Return the fitted pipeline object. Store it in a module-level singleton.
The model trains in < 1 second at startup — fast enough for Render.

Why Logistic Regression instead of Random Forest?
- Returns probabilities natively (predict_proba) — needed for confidence scores
- Has feature_importance via .coef_ — needed for explainability
- Faster to train — suitable for cold starts
- More interpretable — better for explainability
"""

### backend/app/ml/predictor.py
"""
Given input text:
1. sentiment, confidence = predict(text)
   - Use pipeline.predict_proba() for confidence percentage
   - Return: "Positive" | "Negative" | "Neutral"
   - Neutral if confidence < 0.65 (neither clearly positive nor negative)

2. top_words = get_influential_words(text, n=5)
   - Transform text through TF-IDF
   - Multiply TF-IDF weights by model coefficients
   - Return top N words with their influence scores
   - This is the XAI (Explainable AI) feature

Document every step with comments explaining the math.
"""

### backend/app/ml/summarizer.py
"""
Extractive summarization using frequency-based sentence scoring (same algorithm
as the original project, but cleaned up and in its own module):

1. Tokenize text into sentences (nltk sent_tokenize)
2. Tokenize words, remove stopwords, lowercase
3. Build word frequency table
4. Score each sentence by summing frequencies of its words
5. Keep sentences scoring > 1.2 * average (tuned threshold)
6. Return top 2-3 sentences as summary

Also extract keywords:
- Top 5 words by frequency after removing stopwords and punctuation
- Return as list of strings

Also compute stats:
- word_count, sentence_count, reading_time_seconds (words / 200 * 60)
"""

### backend/app/routers/analyze.py
"""
POST /api/v1/analyze

Request body:
{
  "text": "The product quality is amazing...",
  "session_id": "uuid-from-frontend"
}

Validation:
- text: min 20 characters, max 5000 characters
- session_id: valid UUID format

Processing:
1. Clean text (remove emojis, normalize whitespace)
2. Run summarizer → summary, keywords, stats
3. Run predictor → sentiment, confidence, top_words
4. Save to database (analysis history for session)
5. Return full result

Response:
{
  "id": "uuid",
  "sentiment": "Positive",
  "confidence": 0.87,
  "summary": "The product quality is excellent...",
  "keywords": ["quality", "amazing", "delivery", "packaging", "value"],
  "top_influential_words": [
    {"word": "amazing", "score": 0.34},
    {"word": "excellent", "score": 0.28},
    ...
  ],
  "word_count": 142,
  "sentence_count": 8,
  "reading_time_seconds": 43,
  "created_at": "2026-06-06T10:00:00Z"
}
"""

### backend/app/routers/history.py
"""
GET /api/v1/history/{session_id}?limit=10

Returns the last N analyses for a session_id.
Used by the History page in the frontend.

GET /api/v1/history/{session_id}/{analysis_id}

Returns one specific analysis by ID (for deep link sharing).
"""

### backend/app/models/analysis.py
"""
Analysis table:
- id: UUID primary key
- session_id: UUID (no foreign key — anonymous sessions)
- original_text: Text (the input)
- summary: Text
- sentiment: String (Positive/Negative/Neutral)
- confidence: Float
- keywords: JSON (list of strings)
- top_influential_words: JSON (list of {word, score} dicts)
- word_count: Integer
- sentence_count: Integer
- created_at: DateTime with timezone, server_default=now()

Index on session_id for fast history lookup.
"""

### frontend/src/utils/session.js
"""
Generate a UUID and store it in localStorage.
Used to group a user's analyses without requiring login.

function getSessionId() {
  let id = localStorage.getItem('reviewlens_session_id');
  if (!id) {
    id = crypto.randomUUID();  // built into modern browsers
    localStorage.setItem('reviewlens_session_id', id);
  }
  return id;
}
"""

### frontend/src/pages/Home.jsx
"""
Main page with:
- Large textarea: "Paste your product reviews here..."
- Character counter (20 min, 5000 max) shown live
- "Analyze" button — disabled if text < 20 chars
- Loading state with animated spinner
- ResultCard component shown below on success
- Error state with friendly message
- Link to History page
"""

### frontend/src/components/ResultCard.jsx
"""
Shows analysis result:

Top section: Sentiment badge (green=Positive, red=Negative, grey=Neutral)
             Confidence bar (Recharts BarChart, horizontal, 0-100%)

Middle section: Summary (displayed in a quote-style box)

Keywords section: Row of KeywordChip components

XAI section: "Why this prediction?" — list of top influential words
             with their scores shown as small progress bars

Stats section: Word count | Sentence count | Reading time

Bottom: small "Analyzed at [timestamp]" footer
"""

---

## STRICT RULES — MUST FOLLOW EXACTLY

1. EVERY file starts with a module docstring explaining what it does and WHY
2. Every non-obvious line has an inline comment
3. Zero global variables anywhere
4. All secrets in environment variables (.env.example documents them all)
5. Proper error handling everywhere — never expose stack traces to frontend
6. Input validation on backend AND frontend (both sides)
7. All HTTP responses use consistent JSON structure:
   Success: { "data": {...}, "error": null }
   Failure: { "data": null, "error": "message" }
8. Database migrations via Alembic (same pattern as my URL shortener project)
9. The model MUST train at startup — no .sav files, no CSV files in repo
10. README.md must have:
    - Live demo link placeholder
    - What it does in 2 sentences
    - Architecture diagram (Mermaid)
    - Tech stack table
    - Local setup (Windows AND Mac/Linux)
    - Deployment guide (Render + Vercel)
    - API reference (endpoint, request, response)

---

## ENVIRONMENT VARIABLES NEEDED

backend/.env.example:
```
# App
APP_ENV=development

# Database (Supabase Session Pooler URL)
DATABASE_URL=postgresql+asyncpg://postgres.xxxx:password@aws-1-xx.pooler.supabase.com:5432/postgres?ssl=require

# CORS
ALLOWED_ORIGINS=http://localhost:5173
FRONTEND_URL=http://localhost:5173

# API
API_VERSION=v1
```

frontend/.env.example:
```
VITE_API_BASE_URL=http://localhost:8000
```

---

## DEPLOYMENT CONFIGURATION

### Render (backend)
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: cd /opt/render/project/src/backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers

### Vercel (frontend)
Framework: Vite
Environment: VITE_API_BASE_URL=https://your-render-app.onrender.com

vercel.json:
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}

---

## WHAT MAKES THIS STANDOUT FOR A FRESHER

1. FastAPI instead of Django — shows you know modern async Python, not just "Django tutorial"
2. Model trains at startup — no binary files, no version fragility, shows you understand the ML lifecycle
3. XAI (Explainable AI) — returns WHY the model predicted what it did. 99% of fresher ML projects just return a label.
4. Async database — PostgreSQL with async SQLAlchemy, not SQLite in production
5. Session-based history — no login needed but still stores your analysis history. Shows UX thinking.
6. Confidence score with visual bar — not just "Positive", but "Positive (87%)"
7. Proper layered architecture — ml/ services/ routers/ not everything in views.py
8. Deployed and live — anyone can use it immediately

---

## BUILD ORDER

Build in this exact order, completing each file fully before moving on:

1. backend/app/config.py
2. backend/app/database.py  
3. backend/app/models/analysis.py
4. backend/app/schemas/analysis.py
5. backend/app/ml/trainer.py  ← most important, build carefully
6. backend/app/ml/predictor.py
7. backend/app/ml/summarizer.py
8. backend/app/routers/analyze.py
9. backend/app/routers/history.py
10. backend/app/main.py
11. backend/requirements.txt
12. backend/alembic/env.py
13. backend/.env.example
14. frontend/src/utils/session.js
15. frontend/src/api/axios.js
16. frontend/src/components/AnalysisForm.jsx
17. frontend/src/components/ResultCard.jsx
18. frontend/src/components/SentimentBar.jsx
19. frontend/src/components/KeywordChip.jsx
20. frontend/src/pages/Home.jsx
21. frontend/src/pages/History.jsx
22. frontend/src/App.jsx
23. frontend/src/main.jsx
24. frontend/src/index.css  ← dark theme with CSS variables
25. frontend/index.html
26. frontend/package.json
27. frontend/vite.config.js
28. frontend/vercel.json
29. README.md
30. .gitignore

Do NOT skip any file. Do NOT use placeholder comments like "# add code here".
Write the complete, working, commented code for every file.

---

## AFTER BUILDING — TELL ME

1. What is TF-IDF and how does it work in simple terms
2. What is Logistic Regression and why it is better than Random Forest for this use case
3. What is XAI (Explainable AI) and how to explain it in an interview
4. What questions an interviewer will ask about this project
5. What the confidence score calculation means mathematically
6. How extractive summarization differs from abstractive summarization (ChatGPT style)

---

## SAMPLE TRAINING DATA TO USE IN trainer.py

Use these exact 20 positive and 20 negative reviews (you can add more similar ones to reach 60):

POSITIVE:
- "The product quality is absolutely amazing, exceeded my expectations completely."
- "Fast delivery and excellent packaging, the item arrived in perfect condition."
- "Great value for money, highly recommend this product to everyone."
- "The build quality is superb and the performance is outstanding."
- "Customer service was very helpful and resolved my issue immediately."
- "Exactly as described, works perfectly and looks great."
- "Best purchase I have made in a long time, very satisfied."
- "Incredible product, fast shipping, and great customer support."
- "The quality is top notch and it arrived earlier than expected."
- "Very happy with this purchase, the product is exactly what I needed."
- "Brilliant product, works flawlessly and the design is elegant."
- "Superb quality at a very reasonable price point."
- "Delivery was prompt and the packaging was very secure."
- "The product performs exactly as advertised, no complaints at all."
- "Outstanding quality and very durable, well worth the price."
- "Loved the product, it is exactly what I was looking for."
- "Very impressed with the quality and the fast shipping."
- "The item is exactly as shown in the pictures, very satisfied."
- "Great product, great price, great service, highly recommended."
- "Works perfectly straight out of the box, very happy with this purchase."

NEGATIVE:
- "Terrible quality, the product broke within a week of use."
- "Very disappointed, the item looks nothing like the pictures shown."
- "The delivery took forever and the packaging was completely damaged."
- "Waste of money, the product stopped working after two days."
- "Very poor quality, not worth the price at all."
- "Arrived damaged and customer service was completely unhelpful."
- "The product is fake and nowhere near the quality advertised."
- "Extremely disappointed, this is not what I ordered at all."
- "The worst product I have ever bought, total waste of money."
- "Poor build quality and it started falling apart immediately."
- "The description was completely misleading, very unhappy with this."
- "Do not buy this, the quality is absolutely horrible."
- "Returned the product immediately, it was completely defective."
- "Very bad experience, the seller was unresponsive and unhelpful."
- "The product is a complete disappointment, does not work at all."
- "Cheap plastic that broke on first use, terrible quality."
- "Extremely slow delivery and the item arrived badly damaged."
- "Not worth even a single rupee, complete waste of money."
- "The worst purchase ever, totally useless product."
- "Very unhappy, the product does not match the description at all."

---
