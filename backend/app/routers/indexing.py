"""Indexing control endpoints"""

import logging
from fastapi import APIRouter, HTTPException

from ..models.indexing import IndexingStatus, IndexingProgress
from ..services import IndexingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/indexing", tags=["indexing"])

# Service instance (will be initialized in main.py)
indexing_service: IndexingService = None


@router.post("/start")
async def start_indexing():
    """
    Start the indexing process

    Returns:
        Success message
    """
    try:
        if not indexing_service:
            raise HTTPException(status_code=500, detail="Indexing service not initialized")

        started = await indexing_service.start_indexing()

        if not started:
            raise HTTPException(
                status_code=409, detail="Indexing is already in progress"
            )

        logger.info("Indexing process started")
        return {"message": "Indexing started successfully", "status": "in_progress"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting indexing: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error starting indexing: {str(e)}"
        )


@router.post("/stop")
async def stop_indexing():
    """
    Stop the indexing process

    Returns:
        Success message
    """
    try:
        if not indexing_service:
            raise HTTPException(status_code=500, detail="Indexing service not initialized")

        indexing_service.stop_indexing()

        logger.info("Indexing process stopped")
        return {"message": "Indexing stopped successfully"}

    except Exception as e:
        logger.error(f"Error stopping indexing: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error stopping indexing: {str(e)}"
        )


@router.get("/status", response_model=IndexingStatus)
async def get_indexing_status():
    """
    Get current indexing status and metadata

    Returns:
        IndexingStatus object
    """
    try:
        if not indexing_service:
            raise HTTPException(status_code=500, detail="Indexing service not initialized")

        status = indexing_service.get_status()
        return status

    except Exception as e:
        logger.error(f"Error getting indexing status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error getting indexing status: {str(e)}"
        )


@router.get("/progress", response_model=IndexingProgress)
async def get_indexing_progress():
    """
    Get real-time indexing progress (if indexing is in progress)

    Returns:
        IndexingProgress object or None
    """
    try:
        if not indexing_service:
            raise HTTPException(status_code=500, detail="Indexing service not initialized")

        progress = indexing_service.get_progress()

        if not progress:
            raise HTTPException(status_code=404, detail="No indexing in progress")

        return progress

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting indexing progress: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error getting indexing progress: {str(e)}"
        )
