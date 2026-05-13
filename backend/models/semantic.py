"""
Semantic data models.
Represents extracted semantic units from documents — the atomic knowledge pieces.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SemanticUnitType(str, Enum):
    CLAIM = "claim"
    METHODOLOGY = "methodology"
    METRIC = "metric"
    DEFINITION = "definition"
    EQUATION = "equation"
    OBSERVATION = "observation"
    HYPOTHESIS = "hypothesis"
    LIMITATION = "limitation"
    EXPERIMENTAL_RESULT = "experimental_result"


class Section(BaseModel):
    """A section within a document."""
    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex[:12])
    document_id: str
    title: str
    level: int = 1  # heading level (1 = h1, 2 = h2, etc.)
    content: str
    content_hash: str = ""
    order: int = 0
    parent_section_id: Optional[str] = None


class SemanticUnit(BaseModel):
    """An atomic semantic unit extracted from a document section."""
    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex[:12])
    document_id: str
    section_id: str
    unit_type: SemanticUnitType
    content: str
    normalized_content: str = ""  # for deduplication and matching
    confidence: float = 1.0
    embedding: Optional[list[float]] = None
    page_references: list[int] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class Keyphrase(BaseModel):
    """An extracted keyphrase with relevance score."""
    text: str
    score: float = 0.0
    unit_type: Optional[SemanticUnitType] = None


class NamedEntity(BaseModel):
    """A named entity extracted from text."""
    text: str
    label: str  # PERSON, ORG, LOC, DATE, SCIENTIFIC_TERM, etc.
    confidence: float = 0.0