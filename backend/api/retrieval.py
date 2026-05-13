"""
API endpoints for scholarly retrieval functionality.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
import logging

from backend.retrieval.scholarly import scholarly_retriever, RetrievalMode

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.post("/search")
async def search_scholarly(
    query: str,
    mode: RetrievalMode = RetrievalMode.RELATED_WORK,
    top_k: int = 10,
    document_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Perform scholarly search with specialized retrieval modes.
    
    Args:
        query: Search query string
        mode: Retrieval mode (related_work, methodology, etc.)
        top_k: Number of results to return
        document_id: Optional filter for specific document
        
    Returns:
        List of retrieval results with id, score, text, metadata
    """
    try:
        results = await scholarly_retriever.search(
            query=query,
            mode=mode,
            top_k=top_k,
            document_id=document_id,
        )
        return results
    except Exception as e:
        logger.error(f"Retrieval search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@router.get("/modes")
async def get_retrieval_modes() -> List[str]:
    """
    Get available scholarly retrieval modes.
    
    Returns:
        List of available retrieval mode names
    """
    return [mode.value for mode in RetrievalMode]