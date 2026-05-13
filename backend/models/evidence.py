"""
Evidence data models.
Represents evidence units — verified claim-evidence pairs with provenance.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EvidenceRole(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    NEUTRAL = "neutral"
    WEAKENS = "weakens"
    STRENGTHENS = "strengthens"


class VerificationMethod(str, Enum):
    LEXICAL = "lexical"
    SEMANTIC = "semantic"
    NUMERICAL = "numerical"
    CONSENSUS = "consensus"
    CITATION = "citation"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNVERIFIED = "unverified"


class EvidenceUnit(BaseModel):
    """A verified evidence unit linking a claim to a source."""
    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex[:12])
    claim_id: str
    source_document_id: str
    source_section_id: str
    source_semantic_unit_id: str
    content: str  # the supporting/contradicting text from source
    role: EvidenceRole = EvidenceRole.SUPPORTS
    confidence: float = 0.0
    verification_method: VerificationMethod = VerificationMethod.LEXICAL
    verification_score: float = 0.0
    page_reference: Optional[int] = None
    citation_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class EvidenceConsolidation(BaseModel):
    """Consolidated evidence for a single claim from multiple sources."""
    claim_id: str
    claim_text: str
    supporting_evidence: list[EvidenceUnit] = Field(default_factory=list)
    contradicting_evidence: list[EvidenceUnit] = Field(default_factory=list)
    neutral_evidence: list[EvidenceUnit] = Field(default_factory=list)
    consensus_confidence: float = 0.0
    overall_confidence: ConfidenceLevel = ConfidenceLevel.UNVERIFIED
    provenance_chain: list[str] = Field(default_factory=list)  # document_id chain