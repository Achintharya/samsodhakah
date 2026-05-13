"""
API endpoints for verification functionality with user experience enhancements.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
import logging
from pydantic import BaseModel

from backend.verification.ux import verification_ui

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/verification", tags=["verification"])


class SectionClaimsRequest(BaseModel):
    document_id: str
    section_content: str
    section_type: str
    related_work_id: Optional[str] = None


class ClaimFeedbackRequest(BaseModel):
    claim: str
    verification_result: Dict[str, Any]


@router.post("/section-claims")
async def verify_section_claims(request: SectionClaimsRequest) -> Dict[str, Any]:
    """
    Verify claims in section content against source documents.
    
    Args:
        document_id: ID of the source document
        section_content: Content of the section to verify
        section_type: Type of section (methodology, results, etc.)
        related_work_id: Optional related work document ID
        
    Returns:
        Enhanced verification results with user-friendly feedback
    """
    try:
        result = await verification_ui.verify_section_claims(
            document_id=request.document_id,
            section_content=request.section_content,
            section_type=request.section_type,
            related_work_id=request.related_work_id,
        )
        return result
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.post("/claim-feedback")
async def get_claim_feedback(request: ClaimFeedbackRequest) -> Dict[str, Any]:
    """
    Get detailed feedback for a single claim.
    
    Args:
        claim: The claim text
        verification_result: Verification result for this claim
        
    Returns:
        Detailed feedback for UI display
    """
    try:
        feedback = verification_ui.get_claim_feedback(request.claim, request.verification_result)
        return feedback
    except Exception as e:
        logger.error(f"Claim feedback generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Claim feedback generation failed: {str(e)}")


@router.get("/verdicts")
async def get_verdict_info() -> Dict[str, Any]:
    """
    Get information about verification verdicts.
    
    Returns:
        Information about each verdict type
    """
    return {
        "verdicts": {
            "supported": {
                "description": "Claim is well-supported by evidence",
                "color": "green",
                "icon": "✓"
            },
            "partially_supported": {
                "description": "Claim has partial support with some limitations",
                "color": "yellow", 
                "icon": "⚠"
            },
            "contradicted": {
                "description": "Evidence contradicts this claim",
                "color": "red",
                "icon": "✗"
            },
            "unsupported": {
                "description": "No supporting evidence found for claim",
                "color": "orange",
                "icon": "⚠"
            },
            "unverifiable": {
                "description": "Claim cannot be verified with available information",
                "color": "gray",
                "icon": "?"
            }
        }
    }