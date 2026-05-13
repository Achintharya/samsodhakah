"""
DOCX Parser — extraction of academic documents using python-docx.
"""

from __future__ import annotations
import logging
import re
from typing import Optional, Dict, List
from pathlib import Path
from docx import Document
from backend.ingestion.parsers.base import DocumentParser, ParseResult

logger = logging.getLogger(__name__)

class DOCXParser(DocumentParser):
    """
    DOCX Parser for extracting headings, paragraphs, citations, and tables.
    """

    def can_parse(self, filename: str, content: bytes) -> bool:
        """Check if file is a DOCX."""
        return filename.lower().endswith('.docx')

    def parse(self, filename: str, content: bytes) -> Optional[ParseResult]:
        """
        Parse DOCX file and extract sections, headings, and content.
        """
        try:
            doc = Document(content)
            raw_text = ""
            sections = []
            current_section = {
                "title": "",
                "content": "",
                "level": 0,
                "order": 0
            }
            section_order = 0

            # Extract title from document properties
            title = doc.core_properties.title or "Untitled Document"

            # Process each paragraph and heading
            for i, paragraph in enumerate(doc.paragraphs):
                text = paragraph.text.strip()

                # Check for headings based on style
                if paragraph.style.name.startswith('Heading'):
                    level = int(paragraph.style.name.split('Heading')[1])
                    if current_section["content"]:
                        sections.append(current_section)
                    current_section = {
                        "title": text,
                        "content": "",
                        "level": level,
                        "order": section_order
                    }
                    section_order += 1
                else:
                    if current_section["content"]:
                        current_section["content"] += "\n" + text
                    else:
                        current_section["content"] = text

                raw_text += text + "\n"

            # Add the last section if it exists
            if current_section["content"]:
                sections.append(current_section)

            return ParseResult(
                filename=filename,
                title=title,
                raw_text=raw_text,
                sections=sections,
                metadata={
                    "parser": "python-docx",
                    "confidence": 0.95
                }
            )
        except Exception as e:
            logger.error(f"DOCX parsing failed for {filename}: {e}")
            return None