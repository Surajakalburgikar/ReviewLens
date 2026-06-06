"""
Main FastAPI Application Entrypoint.
Handles app lifespan setup (NLTK downloads and ML training),
CORS settings, routing assemblies, and root status endpoints.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import analyze, history

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    App lifespan context manager. Handles startup and shutdown processes.
    - Downloads NLTK corpora packages if missing (punkt, punkt_tab, stopwords).
    - Fits the machine learning model pipeline inline at startup.
    - Auto-creates SQLite tables locally for frictionless local dev.
    """
    logger.info("Initializing ReviewLens service startup processes...")

    # 1. Ensure NLTK resources are present
    # NOTE: Newer NLTK versions use 'punkt_tab' instead of 'punkt'.
    # We download both so the app works across all NLTK versions.
    import nltk
    nltk_resources = [
        ("punkt",     "tokenizers/punkt"),
        ("punkt_tab", "tokenizers/punkt_tab"),
        ("stopwords", "corpora/stopwords"),
    ]
    for name, path in nltk_resources:
        try:
            nltk.data.find(path)
            logger.info(f"NLTK resource '{name}' already available.")
        except Exception:
            logger.info(f"Downloading NLTK resource '{name}'...")
            try:
                nltk.download(name, quiet=True)
            except Exception as e:
                logger.error(f"Failed to download NLTK resource '{name}': {e}")

    # 2. Train the machine learning model inline at startup
    from app.ml.trainer import train_model
    train_model()

    # 3. Auto-create tables when using local SQLite (dev only)
    if settings.DATABASE_URL.startswith("sqlite"):
        logger.info("Local SQLite detected — auto-creating tables...")
        from app.database import Base, engine
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")

    yield
    logger.info("Shutting down ReviewLens service...")


# Initialize FastAPI App
app = FastAPI(
    title="ReviewLens API",
    description="Asynchronous NLP API providing sentiment analysis, XAI explanations, and summaries.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — explicitly list allowed methods and headers (not wildcard *)
# allow_credentials=True is required for cookies to work cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],   # only what the app actually uses
    allow_headers=["Content-Type", "X-Session-ID"],
)

# Assemble versioned API router
api_router = APIRouter(prefix=f"/api/{settings.API_VERSION}")
api_router.include_router(analyze.router, tags=["Analysis"])
api_router.include_router(history.router, tags=["History"])
app.include_router(api_router)


@app.get("/", tags=["Health"])
async def root_status():
    """Base health check endpoint."""
    return {
        "status": "online",
        "service": "ReviewLens API",
        "api_version": settings.API_VERSION,
        "environment": settings.APP_ENV,
    }
