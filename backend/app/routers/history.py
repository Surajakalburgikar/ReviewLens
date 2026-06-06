"""
FastAPI router for session analysis history.
Exposes GET /api/v1/history/{session_id} and GET /api/v1/history/{session_id}/{analysis_id}.
Retrieves past analysis records from the database.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.analysis import Analysis
from app.schemas.analysis import HistoryAPIResponse, AnalysisAPIResponse, AnalysisResult

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/history/{session_id}",
    response_model=HistoryAPIResponse,
    status_code=status.HTTP_200_OK
)
async def get_session_history(
    session_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the last N analysis reports for a specific session UUID.
    Useful for showing a 'Recent Analyses' history list without forcing user logins.
    """
    try:
        # Construct async query to filter by session_id, ordered by creation time descending
        stmt = (
            select(Analysis)
            .filter(Analysis.session_id == session_id)
            .order_by(Analysis.created_at.desc())
            .limit(limit)
        )
        
        result = await db.execute(stmt)
        analyses_orm = result.scalars().all()
        
        # Validate ORM records against schema
        analyses_list = [AnalysisResult.model_validate(item) for item in analyses_orm]
        
        return HistoryAPIResponse(data=analyses_list, error=None)
        
    except Exception as e:
        logger.error(f"Error fetching session history for {session_id}: {str(e)}", exc_info=True)
        return HistoryAPIResponse(
            data=[],
            error="Failed to load your analysis history. Please try again later."
        )

@router.get(
    "/history/{session_id}/{analysis_id}",
    response_model=AnalysisAPIResponse,
    status_code=status.HTTP_200_OK
)
async def get_single_analysis(
    session_id: str,
    analysis_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves a single specific analysis record by its ID and session ID.
    Enables deep link sharing or focusing on a specific past analysis.
    """
    try:
        stmt = (
            select(Analysis)
            .filter(Analysis.session_id == session_id)
            .filter(Analysis.id == analysis_id)
        )
        
        result = await db.execute(stmt)
        analysis_orm = result.scalars().first()
        
        if not analysis_orm:
            return AnalysisAPIResponse(
                data=None,
                error="The requested analysis report was not found."
            )
            
        res = AnalysisResult.model_validate(analysis_orm)
        return AnalysisAPIResponse(data=res, error=None)
        
    except Exception as e:
        logger.error(f"Error fetching analysis {analysis_id}: {str(e)}", exc_info=True)
        return AnalysisAPIResponse(
            data=None,
            error="An error occurred while loading this report."
        )
