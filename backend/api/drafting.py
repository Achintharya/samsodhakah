"""
API endpoints for research drafting functionality.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from typing import Optional, List, Dict, Any
import logging
from pydantic import BaseModel

from backend.drafting.drafting_workflow import drafting_workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/drafting", tags=["drafting"])


@router.post("/outline")
async def generate_section_outline(
    document_id: str,
    section_type: str,
    topic: str,
    related_work_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a structured outline for a research paper section.
    
    Args:
        document_id: ID of the source document
        section_type: Type of section (related_work, methodology, results, etc.)
        topic: Main topic to cover
        related_work_id: Optional related work document ID
        
    Returns:
        Section outline with structure and key points
    """
    try:
        outline = await drafting_workflow.generate_section_outline(
            document_id=document_id,
            section_type=section_type,
            topic=topic,
            related_work_id=related_work_id,
        )
        return outline
    except Exception as e:
        logger.error(f"Outline generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Outline generation failed: {str(e)}")


class SectionRequest(BaseModel):
    document_id: str
    section_type: str
    topic: str
    related_work_id: Optional[str] = None
    max_tokens: Optional[int] = None

@router.post("/section")
async def generate_grounded_section(request: SectionRequest) -> Dict[str, Any]:
    """
    Generate a grounded research section with evidence and citation support.
    
    Args:
        document_id: ID of the source document
        section_type: Type of section (related_work, methodology, results, etc.)
        topic: Main topic to cover
        related_work_id: Optional related work document ID
        max_tokens: Optional override for token limit
        
    Returns:
        Generated section with evidence tracking and citation links
    """
    try:
        section = await drafting_workflow.generate_grounded_section(
            document_id=request.document_id,
            section_type=request.section_type,
            topic=request.topic,
            related_work_id=request.related_work_id,
            max_tokens=request.max_tokens,
        )
        return section
    except Exception as e:
        logger.error(f"Section generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Section generation failed: {str(e)}")


@router.get("/section-types")
async def get_section_types() -> List[str]:
    """
    Get available section types for drafting.
    
    Returns:
        List of available section type names
    """
    return [
        "related_work",
        "methodology", 
        "theory",
        "results",
        "experimental_setup",
        "discussion",
        "abstract",
        "conclusion"
    ]