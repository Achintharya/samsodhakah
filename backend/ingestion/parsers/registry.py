"""
Parser registry — discovers available document parsers and routes documents to the correct one.
"""

from __future__ import annotations

from typing import Optional
import logging

from backend.ingestion.parsers.base import DocumentParser, ParseResult
from backend.ingestion.parsers.markdown_parser import MarkdownParser
from backend.ingestion.parsers.txt_parser import TxtParser
from backend.ingestion.parsers.pdf_parser import PDFParser
from backend.ingestion.parsers.docx_parser import DOCXParser

logger = logging.getLogger(__name__)

class ParserRegistry:
    """Registry of available document parsers with auto-discovery."""

    def __init__(self) -> None:
        self._parsers: list[DocumentParser] = []

        # Register built-in parsers
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register all built-in parsers."""
        self.register(MarkdownParser())
        self.register(TxtParser())
        self.register(PDFParser())
        self.register(DOCXParser())
        logger.info(f"Parser registry initialized with {len(self._parsers)} parsers")

    def register(self, parser: DocumentParser) -> None:
        """Register a new parser."""
        self._parsers.append(parser)
        logger.debug(f"Registered parser: {parser.__class__.__name__}")

    def get_parser(self, filename: str, content: bytes) -> Optional[DocumentParser]:
        """Find a parser that can handle the given file."""
        for parser in self._parsers:
            if parser.can_parse(filename, content):
                return parser
        return None

    def parse(self, filename: str, content: bytes) -> Optional[ParseResult]:
        """Parse a document using the first matching parser."""
        parser = self.get_parser(filename, content)
        if parser is None:
            logger.warning(f"No parser found for file: {filename}")
            return None
        return parser.parse(filename, content)

# Global registry instance
parser_registry = ParserRegistry()