"""
Plain text parser — extracts content from .txt files as a single section.
"""

from __future__ import annotations

from pathlib import Path
import logging

from backend.ingestion.parsers.base import DocumentParser, ParseResult, ParsedSection

logger = logging.getLogger(__name__)


class TxtParser(DocumentParser):
    """Parser for plain text (.txt) files."""

    def can_parse(self, filename: str, content: bytes) -> bool:
        return filename.lower().endswith(".txt")

    def parse(self, filename: str, content: bytes) -> ParseResult:
        text = content.decode("utf-8", errors="replace")
        lines = text.split("\n")
        title = lines[0].strip() if lines else Path(filename).stem

        # Use first line as title if it looks like one
        first_line = lines[0].strip() if lines else ""
        if first_line and len(first_line) < 200:
            title = first_line
            body = "\n".join(lines[1:]).strip()
        else:
            title = Path(filename).stem
            body = text.strip()

        sections = [
            ParsedSection(
                title=title,
                content=body or text.strip(),
                level=1,
                order=0,
            )
        ]

        result = ParseResult(
            filename=filename,
            title=title,
            sections=sections,
            metadata={},
            raw_text=text,
        )

        logger.info(f"Parsed text file '{filename}': {len(text)} characters")
        return result