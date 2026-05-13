"""
Parser abstraction layer.
Defines the interface for all document parsers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import hashlib


@dataclass
class ParsedSection:
    """A single section extracted from a document."""
    title: str
    content: str
    level: int  # heading depth (1 = h1, 2 = h2, etc.)
    order: int  # position in document
    parent_title: Optional[str] = None

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()[:16]


@dataclass
class ParseResult:
    """The full result of parsing a document."""
    filename: str
    title: Optional[str] = None
    sections: list[ParsedSection] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    raw_text: str = ""

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.raw_text.encode("utf-8")).hexdigest()[:16]


class DocumentParser(ABC):
    """Abstract base class for all document parsers."""

    @abstractmethod
    def can_parse(self, filename: str, content: bytes) -> bool:
        """Check if this parser can handle the given file."""
        ...

    @abstractmethod
    def parse(self, filename: str, content: bytes) -> ParseResult:
        """Parse a document and return structured sections."""
        ...