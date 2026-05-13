"""
Citation data models.
Represents citations, references, and bibliography entries.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class CitationStyle(str, Enum):
    IEEE = "ieee"
    ACM = "acm"
    APA = "apa"
    SPRINGER = "springer"
    NATURE = "nature"


class Citation(BaseModel):
    """A citation extracted from a document."""
    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex[:12])
    document_id: str
    raw_text: str  # the original citation text as found
    authors: list[str] = Field(default_factory=list)
    title: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    publisher: Optional[str] = None
    citation_index: int = 0  # position in the reference list
    confidence: float = 0.0


class ReferenceEntry(BaseModel):
    """A formatted bibliography entry."""
    citation_id: str
    formatted_text: str  # already formatted in the target style
    style: CitationStyle = CitationStyle.IEEE
    key: str = ""  # citation key (e.g., [1], Smith2023)