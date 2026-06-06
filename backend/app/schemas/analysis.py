"""
Pydantic schema definitions for ReviewLens analysis requests and responses.
Provides strict validation on request text and consistent structure on output.
"""
from typing import List, Dict, Optional, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field, UUID4, field_validator

# Define a generic data type for standard API responses
T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    """
    Standard envelope format for all API responses.
    """
    data: Optional[T] = None
    error: Optional[str] = None

class AnalysisRequest(BaseModel):
    """
    Incoming request to analyze a review.
    """
    text: str = Field(
        ...,
        min_length=20,
        max_length=5000,
        description="The product review text to analyze. Must be between 20 and 5000 characters."
    )
    session_id: str = Field(
        ...,
        description="Anonymous session UUID to associate this analysis with a user history."
    )

    # Validate UUID format
    @field_validator("session_id")
    @classmethod
    def validate_uuid(cls, value: str) -> str:
        import uuid
        try:
            uuid.UUID(value)
        except ValueError:
            raise ValueError("session_id must be a valid UUID v4 string.")
        return value

class InfluentialWord(BaseModel):
    """
    Indicates how much a word influenced the prediction (XAI score).
    """
    word: str
    score: float

class AnalysisResult(BaseModel):
    """
    The full report details of an analyzed review.
    """
    id: str
    sentiment: str
    confidence: float
    summary: str
    keywords: List[str]
    top_influential_words: List[InfluentialWord]
    word_count: int
    sentence_count: int
    reading_time_seconds: int
    created_at: datetime

    class Config:
        from_attributes = True

# Specific response schema aliases for clearer OpenAPI docs
class AnalysisAPIResponse(APIResponse[AnalysisResult]):
    pass

class HistoryAPIResponse(APIResponse[List[AnalysisResult]]):
    pass
