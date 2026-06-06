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
    - Downloads NLTK corpora packages (punkt and stopwords) if missing.
    - Fits the machine learning model pipeline inline at startup.
    - Auto-creates SQLite tables locally for frictionless onboarding.
    """
    logger.info("Initializing ReviewLens service startup processes...")
    
    # 1. Ensure NLTK resources are loaded
    import nltk
    for resource in ["punkt", "stopwords"]:
        try:
            if resource == "punkt":
                nltk.data.find("tokenizers/punkt")
            else:
                nltk.data.find("corpora/stopwords")
            logger.info(f"NLTK resource '{resource}' already available.")
        except LookupError:
            logger.info(f"Downloading NLTK resource '{resource}'...")
            nltk.download(resource, quiet=True)
            
    # 2. Train the machine learning model inline
    from app.ml.trainer import train_model
    train_model()
    
    # 3. Create tables automatically if using a local SQLite file
    if settings.DATABASE_URL.startswith("sqlite"):
        logger.info("Local SQLite database detected. Automating table creation...")
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
    lifespan=lifespan
)

# Set up CORS Middleware (allows Vercel deployments and localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Assemble API version router
api_router = APIRouter(prefix=f"/api/{settings.API_VERSION}")
api_router.include_router(analyze.router, tags=["Analysis"])
api_router.include_router(history.router, tags=["History"])

# Register routers
app.include_router(api_router)

@app.get("/", tags=["Health"])
async def root_status():
    """
    Base status check endpoint.
    """
    return {
        "status": "online",
        "service": "ReviewLens API",
        "api_version": settings.API_VERSION,
        "environment": settings.APP_ENV
    }
