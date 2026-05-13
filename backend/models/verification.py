"""
Verification result data models.
Represents outputs of the multi-stage verification engine.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from backend.models.evidence import EvidenceRole, VerificationMethod, ConfidenceLevel


class ContradictionType(str, Enum):
    DIRECT = "direct"  # directly opposing claims
    NUMERICAL = "numerical"  # conflicting numbers/statistics
    METHODOLOGICAL = "methodological"  # different methodologies
    TEMPORAL = "temporal"  # time-based contradictions
    CONTEXTUAL = "contextual"  # context-dependent


class VerificationResult(BaseModel):
    """Result of verifying a single claim against the evidence base."""
    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex[:12])
    claim_id: str
    claim_text: str
    is_supported: bool = False
    confidence: ConfidenceLevel = ConfidenceLevel.UNVERIFIED
    confidence_score: float = 0.0
    supporting_count: int = 0
    contradicting_count: int = 0
    primary_method: VerificationMethod = VerificationMethod.LEXICAL
    methods_used: list[VerificationMethod] = Field(default_factory=list)
    evidence_summary: str = ""
    contradictions: list[ContradictionEntry] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class ContradictionEntry(BaseModel):
    """A detected contradiction between two claims or sources."""
    claim_id_a: str
    claim_text_a: str
    claim_id_b: str
    claim_text_b: str
    source_a: str  # document_id
    source_b: str
    contradiction_type: ContradictionType = ContradictionType.DIRECT
    severity: float = 0.0  # 0.0 to 1.0
    description: str = ""


class VerificationBatch(BaseModel):
    """A batch of verification results for a draft or set of claims."""
    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex[:12])
    draft_id: Optional[str] = None
    results: list[VerificationResult] = Field(default_factory=list)
    contradictions: list[ContradictionEntry] = Field(default_factory=list)
    overall_support_rate: float = 0.0
    total_claims: int = 0
    supported_claims: int = 0
    unsupported_claims: int = 0
    contradicted_claims: int = 0
    created_at: datetime = Field(default_factory=datetime.now)


class DraftSection(BaseModel):
    """A single section in a generated scientific draft."""
    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex[:12])
    title: str
    content: str
    order: int = 0
    evidence_links: list[EvidenceLink] = Field(default_factory=list)
    confidence: float = 0.0
    token_count: int = 0


class EvidenceLink(BaseModel):
    """Link between a paragraph/claim in a draft and its supporting evidence."""
    paragraph_index: int
    claim_text: str
    evidence_units: list[str] = Field(default_factory=list)  # evidence_unit_ids
    citations: list[str] = Field(default_factory=list)  # citation_ids
    confidence: float = 0.0