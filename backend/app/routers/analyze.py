"""
FastAPI router for review analysis.
Exposes POST /api/v1/analyze. Handles input sanitization, pipeline processing,
database persistence, and error wrapping.
"""
import logging
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisRequest, AnalysisAPIResponse, AnalysisResult
from app.ml.predictor import predict_sentiment, get_influential_words
from app.ml.summarizer import analyze_and_summarize

logger = logging.getLogger(__name__)

router = APIRouter()

def clean_text(text: str) -> str:
    """
    Cleanses input text:
    - Normalizes multiple spaces and newlines
    - Strips non-printable characters and standard emojis
    """
    # Replace newlines/tabs with spaces
    text = re.sub(r'[\r\n\t]+', ' ', text)
    # Remove non-printable characters (keep standard ASCII and unicode letters)
    text = "".join(c for c in text if c.isprintable() or c.isspace())
    # Strip emojis (non-BMP characters)
    text = re.sub(r'[^\u0000-\uFFFF]', '', text)
    # Normalize multiple whitespace characters to a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

@router.post(
    "/analyze",
    response_model=AnalysisAPIResponse,
    status_code=status.HTTP_201_CREATED
)
async def analyze_review(
    payload: AnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to process and analyze a product review:
    1. Sanitizes the raw input text.
    2. Generates an extractive summary, extracts key terms, and computes metrics.
    3. Runs model inference for sentiment prediction and confidence scores.
    4. Computes explainability (XAI) feature weights for the prediction.
    5. Saves the record to PostgreSQL/SQLite asynchronously.
    6. Returns the formatted AnalysisResult.
    """
    try:
        raw_text = payload.text
        
        # 1. Cleanse raw text
        cleaned = clean_text(raw_text)
        
        # Double check character limit bounds after cleaning
        if len(cleaned) < 20:
            return AnalysisAPIResponse(
                data=None,
                error="Review text is too short after cleaning. Must be at least 20 characters."
            )
            
        # 2. Extract summary and metrics
        summary, keywords, stats = analyze_and_summarize(cleaned)
        
        # 3. Predict sentiment classification
        sentiment, confidence = predict_sentiment(cleaned)
        
        # 4. Calculate Explainable AI scores
        top_words = get_influential_words(cleaned, sentiment, n=5)
        
        # 5. Save the analysis record to the database
        db_analysis = Analysis(
            session_id=payload.session_id,
            original_text=cleaned,
            summary=summary,
            sentiment=sentiment,
            confidence=confidence,
            keywords=keywords,
            top_influential_words=top_words,
            word_count=stats["word_count"],
            sentence_count=stats["sentence_count"],
            reading_time_seconds=stats["reading_time_seconds"]
        )
        
        db.add(db_analysis)
        await db.commit()
        await db.refresh(db_analysis)
        
        # 6. Map the ORM object to the response schema and wrap in success envelope
        result = AnalysisResult.model_validate(db_analysis)
        return AnalysisAPIResponse(data=result, error=None)
        
    except Exception as e:
        logger.error(f"Error during analysis processing: {str(e)}", exc_info=True)
        # Prevent internal details leaking in responses
        return AnalysisAPIResponse(
            data=None,
            error="An error occurred while processing your review. Please try again."
        )
