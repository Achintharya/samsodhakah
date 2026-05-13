"""
Evaluation and workflow failure-corpus endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.evaluation.failure_corpus import FAILURE_TYPES, failure_corpus

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


class FailureCaseRequest(BaseModel):
    """Request model for manually recording workflow failure examples."""

    failure_type: str = Field(..., description="Failure category, e.g. poor_retrieval or citation_mismatch.")
    summary: str = Field(..., description="Short human-readable description of the failure.")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Structured debugging payload.")
    severity: str = Field(default="medium", description="low, medium, high, or critical.")
    source: str = Field(default="manual", description="Subsystem or validation run that observed the failure.")


@router.post("/failure-corpus")
async def record_failure_case(request: FailureCaseRequest) -> Dict[str, Any]:
    """Record a failure example for future retrieval/prompt/export tuning."""
    return failure_corpus.record(
        failure_type=request.failure_type,
        summary=request.summary,
        payload=request.payload,
        severity=request.severity,
        source=request.source,
    )


@router.get("/failure-corpus")
async def list_failure_cases(
    failure_type: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """List recent failure examples, newest first."""
    return failure_corpus.list_cases(failure_type=failure_type, limit=min(max(limit, 1), 500))


@router.get("/failure-corpus/summary")
async def get_failure_corpus_summary() -> Dict[str, Any]:
    """Return compact failure-corpus statistics and supported types."""
    summary = failure_corpus.summary()
    summary["supported_failure_types"] = sorted(FAILURE_TYPES)
    return summary
