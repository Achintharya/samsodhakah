"""
Document-level data models.
Represents ingested scientific papers and documents.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"
    TXT = "txt"
    CSV = "csv"
    HTML = "html"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PARSING = "parsing"
    PARSED = "parsed"
    SEMANTIC_EXTRACTION = "semantic_extraction"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    """Metadata extracted from a document."""
    title: Optional[str] = None
    authors: list[str] = Field(default_factory=list)
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None
    language: str = "en"
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    source_url: Optional[str] = None


class Document(BaseModel):
    """Top-level document entity."""
    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex[:12])
    filename: str
    doc_type: DocumentType
    status: DocumentStatus = DocumentStatus.PENDING
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    section_count: int = 0
    semantic_unit_count: int = 0
    file_size_bytes: int = 0
    content_hash: str = ""
    storage_path: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)