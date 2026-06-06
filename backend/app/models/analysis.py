"""
SQLAlchemy database model for stored analyses.
Tracks original text, sentiment, confidence, summary, keywords, stats, and XAI feature details.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    # Primary key UUID
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Session UUID grouping analyses for a user (indexed for fast history retrieval)
    session_id = Column(String(36), index=True, nullable=False)
    
    # Raw user review text
    original_text = Column(Text, nullable=False)
    
    # Extractive summary of the review
    summary = Column(Text, nullable=False)
    
    # Predicted sentiment: Positive, Negative, or Neutral
    sentiment = Column(String(20), nullable=False)
    
    # Confidence score (0.0 to 1.0)
    confidence = Column(Float, nullable=False)
    
    # Key theme terms extracted from reviews (JSON array of strings)
    keywords = Column(JSON, nullable=False)
    
    # Explainable AI words and scores (JSON array of dicts: {"word": str, "score": float})
    top_influential_words = Column(JSON, nullable=False)
    
    # Metric counters and helper metadata
    word_count = Column(Integer, nullable=False)
    sentence_count = Column(Integer, nullable=False)
    reading_time_seconds = Column(Integer, nullable=False)
    
    # Creation timestamp
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
