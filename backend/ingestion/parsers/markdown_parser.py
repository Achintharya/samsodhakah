"""
Markdown parser — extracts sections from .md files using heading detection.
Improved robustness for research paper parsing.
"""

from __future__ import annotations

import re
from pathlib import Path
import logging
from typing import List, Tuple

from backend.ingestion.parsers.base import DocumentParser, ParseResult, ParsedSection

logger = logging.getLogger(__name__)

# Regex to match markdown headings: ## Title, # Title, etc.
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

# Simple frontmatter pattern
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Pattern to identify section dividers (common in research papers)
SECTION_DIVIDER_PATTERN = re.compile(r"^\s*-{3,}\s*$", re.MULTILINE)

# Pattern to identify potential titles at beginning of documents
TITLE_PATTERN = re.compile(r"^(?:#+\s+)?(.+?)$", re.MULTILINE)


class MarkdownParser(DocumentParser):
    """Parser for Markdown (.md) files with improved robustness."""

    def can_parse(self, filename: str, content: bytes) -> bool:
        return filename.lower().endswith(".md")

    def _validate_and_clean_section(self, title: str, content: str, level: int, order: int) -> Tuple[str, str, int]:
        """
        Validate and clean section data to ensure robustness.
        
        Returns:
            Tuple of (cleaned_title, cleaned_content, adjusted_level)
        """
        # Clean title
        cleaned_title = title.strip()
        if not cleaned_title:
            # If title is empty, generate one based on content
            cleaned_title = f"Section_{order}"
            
        # Clean content
        cleaned_content = content.strip()
        
        # Validate/adjust level
        adjusted_level = max(1, min(level, 6))  # Levels should be between 1-6
        
        return cleaned_title, cleaned_content, adjusted_level

    def _extract_sections_robust(self, text: str) -> List[Tuple[str, str, int, int]]:
        """
        Extract sections with robust handling of edge cases.
        
        Returns:
            List of tuples: (title, content, level, order)
        """
        sections = []
        current_title = ""
        current_content: List[str] = []
        current_level = 1
        order = 0
        
        lines = text.split('\n')
        in_multiline_code_block = False
        code_block_delimiter = None
        
        for i, line in enumerate(lines):
            # Handle code blocks (simple detection)
            if line.strip() in ['```', '~~~']:
                if not in_multiline_code_block:
                    in_multiline_code_block = True
                    code_block_delimiter = line.strip()
                elif line.strip() == code_block_delimiter:
                    in_multiline_code_block = False
                    code_block_delimiter = None
            
            # Skip code block lines if inside a code block
            if in_multiline_code_block:
                current_content.append(line)
                continue
                
            heading_match = HEADING_PATTERN.match(line)
            if heading_match:
                # Save previous section if exists
                if current_content:
                    cleaned_title, cleaned_content, adjusted_level = self._validate_and_clean_section(
                        current_title, '\n'.join(current_content), current_level, order
                    )
                    if cleaned_content:  # Only add if there's actual content
                        sections.append((cleaned_title, cleaned_content, adjusted_level, order))
                        order += 1

                current_level = len(heading_match.group(1))
                current_title = heading_match.group(2).strip()
                current_content = []
            else:
                # Handle potential section dividers
                if SECTION_DIVIDER_PATTERN.match(line):
                    # This might be a section divider, treat as content
                    current_content.append(line)
                else:
                    current_content.append(line)

        # Save final section
        if current_content:
            cleaned_title, cleaned_content, adjusted_level = self._validate_and_clean_section(
                current_title, '\n'.join(current_content), current_level, order
            )
            if cleaned_content:  # Only add if there's actual content
                sections.append((cleaned_title, cleaned_content, adjusted_level, order))

        return sections

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

        # Extract sections robustly
        section_data = self._extract_sections_robust(text)
        sections = [
            ParsedSection(
                title=title,
                content=content,
                level=level,
                order=order,
            )
            for title, content, level, order in section_data
        ]

        # If no h1 was found, use filename as title or first section title
        if not title and sections:
            title = sections[0].title if sections[0].level == 1 else Path(filename).stem

        # Add log for ingestion observability
        section_count = len(sections)
        char_count = len(text)

        logger.info(
            f"Parsed markdown '{filename}': "
            f"{section_count} sections, "
            f"{char_count} characters, "
            f"title='{title}'"
        )
        
        # Create log entry for observability
        self._create_ingestion_log(filename, section_count, char_count, title)

        result = ParseResult(
            filename=filename,
            title=title or Path(filename).stem,
            sections=sections,
            metadata=metadata,
            raw_text=text,
        )

        return result

    def _create_ingestion_log(self, filename: str, section_count: int, char_count: int, title: str) -> None:
        """Create log entry for ingestion observability."""
        import json
        import datetime
        from pathlib import Path
        
        # Ensure log directory exists
        log_dir = Path("runtime") / "ingestion_logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "filename": filename,
            "section_count": section_count,
            "character_count": char_count,
            "title": title,
            "status": "success" if section_count > 0 else "warning_no_sections"
        }
        
        # Write to log file
        log_filename = log_dir / f"ingestion_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{Path(filename).stem}.json"
        try:
            with open(log_filename, 'w') as f:
                json.dump(log_entry, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to write ingestion log for {filename}: {e}")
