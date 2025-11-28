"""Confluence information endpoints"""

import logging
from fastapi import APIRouter, HTTPException
from typing import List

from ..models.confluence import ConfluenceSpace
from ..services import ConfluenceService, VectorDBService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/confluence", tags=["confluence"])

# Service instances (will be initialized in main.py)
confluence_service: ConfluenceService = None
vector_db_service: VectorDBService = None


@router.get("/spaces", response_model=List[ConfluenceSpace])
async def get_spaces():
    """
    Get all Confluence spaces with document counts

    Returns:
        List of Confluence spaces
    """
    try:
        if not confluence_service or not vector_db_service:
            raise HTTPException(status_code=500, detail="Services not initialized")

        # Get spaces from Confluence
        spaces = confluence_service.get_all_spaces()

        # Get document counts from vector DB
        spaces_summary = vector_db_service.get_spaces_summary()

        # Update document counts
        for space in spaces:
            # Count chunks for this space in vector DB
            space.document_count = spaces_summary.get(space.key, 0)

        logger.info(f"Retrieved {len(spaces)} Confluence spaces")
        return spaces

    except Exception as e:
        logger.error(f"Error fetching Confluence spaces: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error fetching spaces: {str(e)}"
        )


@router.get("/spaces/{space_key}/count")
async def get_space_document_count(space_key: str):
    """
    Get document count for a specific space

    Args:
        space_key: The space key

    Returns:
        Document count
    """
    try:
        if not confluence_service:
            raise HTTPException(status_code=500, detail="Confluence service not initialized")

        count = confluence_service.get_space_content_count(space_key)

        return {"space_key": space_key, "document_count": count}

    except Exception as e:
        logger.error(f"Error fetching document count for space {space_key}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching document count: {str(e)}"
        )
