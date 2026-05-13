"""
PDF Parser — robust extraction of academic papers using pypdf, pymupdf, and pdfplumber.
"""

from __future__ import annotations
import logging
import re
from typing import Optional, Dict, List, Tuple
from pathlib import Path

from pypdf import PdfReader
import pymupdf
import pdfplumber
from backend.ingestion.parsers.base import DocumentParser, ParseResult

logger = logging.getLogger(__name__)

class PDFParser(DocumentParser):
    """
    PDF Parser with multi-layered extraction:
    1. pypdf for basic text extraction
    2. pymupdf (fitz) for complex layouts
    3. pdfplumber for table extraction
    """

    def __init__(self) -> None:
        self._fallback_extractors = [
            self._extract_with_pypdf,
            self._extract_with_pymupdf,
            self._extract_with_pdfplumber
        ]

    def can_parse(self, filename: str, content: bytes) -> bool:
        """Check if file is a PDF."""
        return filename.lower().endswith('.pdf')

    def parse(self, filename: str, content: bytes) -> Optional[ParseResult]:
        """
        Parse PDF with fallback extraction strategies.
        """
        try:
            # Try direct extraction first
            result = self._extract_with_pypdf(content)
            if result:
                return result

            # Fallback to pymupdf if pypdf fails
            result = self._extract_with_pymupdf(content)
            if result:
                return result

            # Fallback to pdfplumber for complex layouts
            result = self._extract_with_pdfplumber(content)
            if result:
                return result

            logger.warning(f"No successful extraction for {filename}")
            return None

        except Exception as e:
            logger.error(f"PDF parsing failed for {filename}: {e}")
            return None

    def _extract_with_pypdf(self, content: bytes) -> Optional[ParseResult]:
        """Basic extraction using pypdf."""
        try:
            reader = PdfReader(content)
            raw_text = "\n".join([page.extract_text() for page in reader.pages])

            # Simple section detection (very basic)
            sections = self._detect_sections_basic(raw_text)

            return ParseResult(
                title=self._extract_title(raw_text),
                raw_text=raw_text,
                sections=sections,
                metadata={
                    "parser": "pypdf",
                    "confidence": 0.7
                }
            )
        except Exception as e:
            logger.debug(f"pypdf extraction failed: {e}")
            return None

    def _extract_with_pymupdf(self, content: bytes) -> Optional[ParseResult]:
        """Advanced extraction using pymupdf."""
        try:
            doc = pymupdf.open(stream=content, filetype="pdf")
            raw_text = ""
            sections = []

            for page in doc:
                text = page.get_text("text")
                raw_text += text + "\n"

                # Try to detect sections based on text blocks
                blocks = page.get_text("blocks")
                for block in blocks:
                    if block["type"] == 0:  # Text block
                        text_content = block["text"]
                        if text_content.strip():
                            sections.append({
                                "title": text_content[:50] if len(text_content) > 50 else text_content,
                                "content": text_content,
                                "level": 1  # Basic level
                            })

            return ParseResult(
                title=self._extract_title(raw_text),
                raw_text=raw_text,
                sections=sections,
                metadata={
                    "parser": "pymupdf",
                    "confidence": 0.85
                }
            )
        except Exception as e:
            logger.debug(f"pymupdf extraction failed: {e}")
            return None

    def _extract_with_pdfplumber(self, content: bytes) -> Optional[ParseResult]:
        """Table-aware extraction using pdfplumber."""
        try:
            with pdfplumber.open(content) as pdf:
                raw_text = ""
                sections = []

                for page in pdf.pages:
                    text = page.extract_text()
                    raw_text += text + "\n"

                    # Try to extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        table_text = "\n".join(["\t".join(row) for row in table])
                        sections.append({
                            "title": "Table",
                            "content": table_text,
                            "level": 2
                        })

                return ParseResult(
                    title=self._extract_title(raw_text),
                    raw_text=raw_text,
                    sections=sections,
                    metadata={
                        "parser": "pdfplumber",
                        "confidence": 0.9
                    }
                )
        except Exception as e:
            logger.debug(f"pdfplumber extraction failed: {e}")
            return None

    def _extract_title(self, text: str) -> str:
        """Extract title from PDF text using heuristics."""
        # Try to find title in common locations
        title_patterns = [
            r'^.*?Title:?.*?([^\n]+)',
            r'^.*?Title.*?([^\n]+)',
            r'^.*?Abstract.*?([^\n]+)',
            r'^.*?Introduction.*?([^\n]+)',
            r'^.*?1\.?\s*(.*?)\s*\n'
        ]

        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "Untitled Document"

    def _detect_sections_basic(self, text: str) -> List[Dict]:
        """Basic section detection using heading patterns."""
        sections = []
        current_section = {"title": "", "content": "", "level": 1, "order": 0}

        # Simple heading detection
        heading_patterns = {
            1: r'^\s*[A-Z][^.!?]*[.!?]',
            2: r'^\s*\d+\.\s*[^.!?]*[.!?]',
            3: r'^\s*\d+\.\d+\.\s*[^.!?]*[.!?]'
        }

        lines = text.split('\n')
        for i, line in enumerate(lines):
            for level, pattern in heading_patterns.items():
                if re.match(pattern, line):
                    if current_section["content"]:
                        sections.append(current_section)
                    current_section = {
                        "title": line.strip(),
                        "content": "",
                        "level": level,
                        "order": len(sections) + 1
                    }
                    break
            else:
                if current_section["content"]:
                    current_section["content"] += "\n" + line
                else:
                    current_section["content"] = line

        if current_section["content"]:
            sections.append(current_section)

        return sections