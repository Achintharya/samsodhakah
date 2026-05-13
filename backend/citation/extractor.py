"""
Citation extraction — identifies and parses citations from document text.
"""

from __future__ import annotations

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Common citation patterns
IEEE_PATTERN = re.compile(r"\[(\d+)(?:[,\s]*(\d+))?\]")
PAREN_YEAR_PATTERN = re.compile(r"\(([^)]+?,\s*\d{4}[^)]*)\)")
AUTHOR_YEAR_PATTERN = re.compile(r"([A-Z][a-z]+(?:\s+et\s+al\.?)?)\s*\((\d{4})\)")
BIBTEX_KEY_PATTERN = re.compile(r"@\w+\{(\w+),")


class CitationExtractor:
    """Extract and parse citations from scientific document text."""

    def extract(self, text: str, document_id: str) -> list[dict]:
        """
        Extract all citations from a document.

        Args:
            text: Document text content.
            document_id: Source document identifier.

        Returns:
            List of citation dicts with raw_text, format, position info.
        """
        citations = []

        # IEEE-style: [1], [1, 2], [1-3]
        for match in IEEE_PATTERN.finditer(text):
            citations.append({
                "document_id": document_id,
                "raw_text": match.group(),
                "format": "ieee",
                "citation_index": int(match.group(1)),
                "position": match.start(),
            })

        # Author-year: (Smith, 2023)
        for match in PAREN_YEAR_PATTERN.finditer(text):
            citations.append({
                "document_id": document_id,
                "raw_text": match.group(),
                "format": "author_year",
                "position": match.start(),
            })

        # Author et al. (2023)
        for match in AUTHOR_YEAR_PATTERN.finditer(text):
            citations.append({
                "document_id": document_id,
                "raw_text": match.group(),
                "format": "author_year_narrative",
                "author": match.group(1),
                "year": int(match.group(2)),
                "position": match.start(),
            })

        # Deduplicate by raw_text
        seen = set()
        unique = []
        for c in citations:
            if c["raw_text"] not in seen:
                seen.add(c["raw_text"])
                unique.append(c)

        logger.info(f"Extracted {len(unique)} citations from document {document_id}")
        return unique

    def extract_references_section(self, text: str) -> list[dict]:
        """
        Extract the references section and parse individual references.

        Args:
            text: Full document text.

        Returns:
            List of individual reference entries.
        """
        # Find references section
        ref_patterns = [
            r"(?:REFERENCES|REFERENCES\s+\[\d+\]|BIBLIOGRAPHY|WORKS\s+CITED)",
        ]

        ref_start = -1
        for pattern in ref_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ref_start = match.start()
                break

        if ref_start == -1:
            return []

        ref_text = text[ref_start:]

        # Split into individual references
        # Common patterns: [1] ..., 1. ..., [Author], ...
        refs = []
        current_ref = ""

        for line in ref_text.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Check if this line starts a new reference
            if re.match(r"^\[\d+\]", line) or re.match(r"^\d+\.\s", line):
                if current_ref:
                    refs.append(current_ref.strip())
                current_ref = line
            else:
                current_ref += " " + line

        if current_ref:
            refs.append(current_ref.strip())

        return refs


citation_extractor = CitationExtractor()