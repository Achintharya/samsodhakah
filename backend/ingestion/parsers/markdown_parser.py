"""
Markdown parser — extracts sections from .md files using heading detection.
"""

from __future__ import annotations

import re
from pathlib import Path
import logging

from backend.ingestion.parsers.base import DocumentParser, ParseResult, ParsedSection

logger = logging.getLogger(__name__)

# Regex to match markdown headings: ## Title, # Title, etc.
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

# Simple frontmatter pattern
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


class MarkdownParser(DocumentParser):
    """Parser for Markdown (.md) files."""

    def can_parse(self, filename: str, content: bytes) -> bool:
        return filename.lower().endswith(".md")

    def parse(self, filename: str, content: bytes) -> ParseResult:
        text = content.decode("utf-8", errors="replace")
        metadata = {}

        # Extract YAML frontmatter if present
        frontmatter_match = FRONTMATTER_PATTERN.match(text)
        if frontmatter_match:
            raw_frontmatter = frontmatter_match.group(1)
            metadata["frontmatter"] = raw_frontmatter
            for line in raw_frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip().lower()] = value.strip().strip('"').strip("'")
            text = text[frontmatter_match.end() :]

        # Extract title from first h1 or filename
        title = metadata.get("title", None)

        # Split text into sections based on headings
        sections: list[ParsedSection] = []
        current_title = ""
        current_content: list[str] = []
        current_level = 1
        order = 0

        lines = text.split("\n")
        for line in lines:
            heading_match = HEADING_PATTERN.match(line)
            if heading_match:
                # Save previous section
                if current_content:
                    sections.append(ParsedSection(
                        title=current_title,
                        content="\n".join(current_content).strip(),
                        level=current_level,
                        order=order,
                    ))
                    order += 1

                current_level = len(heading_match.group(1))
                current_title = heading_match.group(2).strip()
                current_content = []
            else:
                current_content.append(line)

        # Save final section
        if current_content:
            sections.append(ParsedSection(
                title=current_title,
                content="\n".join(current_content).strip(),
                level=current_level,
                order=order,
            ))

        # If no h1 was found, use filename as title
        if not title and sections:
            title = sections[0].title if sections[0].level == 1 else Path(filename).stem

        result = ParseResult(
            filename=filename,
            title=title or Path(filename).stem,
            sections=sections,
            metadata=metadata,
            raw_text=text,
        )

        logger.info(
            f"Parsed markdown '{filename}': "
            f"{len(sections)} sections, "
            f"{len(text)} characters"
        )
        return result