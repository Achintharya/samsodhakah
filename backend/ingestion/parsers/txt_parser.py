"""
Plain text parser — extracts content from .txt files as a single section.
Improved robustness for research paper parsing.
"""

from __future__ import annotations

from pathlib import Path
import logging
from typing import List

from backend.ingestion.parsers.base import DocumentParser, ParseResult, ParsedSection

logger = logging.getLogger(__name__)


class TxtParser(DocumentParser):
    """Parser for plain text (.txt) files with improved robustness."""

    def can_parse(self, filename: str, content: bytes) -> bool:
        return filename.lower().endswith(".txt")

    def _extract_title_and_body(self, lines: List[str]) -> tuple[str, str]:
        """
        Extract title and body from text lines with robust handling.
        
        Returns:
            Tuple of (title, body)
        """
        # Handle empty file
        if not lines:
            return Path(filename).stem, ""
            
        # Try to extract title from first line if it looks like a title
        first_line = lines[0].strip()
        if first_line and len(first_line) < 200 and not first_line.startswith('#'):
            # Check if it's likely a title (not code, not very short, not a date/time)
            if len(first_line) > 5 and not first_line.startswith('[') and not first_line.endswith(':'):
                title = first_line
                body = "\n".join(lines[1:]).strip()
            else:
                title = Path(filename).stem
                body = "\n".join(lines).strip()
        else:
            title = Path(filename).stem
            body = "\n".join(lines).strip()
            
        return title, body

    def parse(self, filename: str, content: bytes) -> ParseResult:
        text = content.decode("utf-8", errors="replace")
        lines = text.split("\n")
        
        # Extract title and body robustly
        title, body = self._extract_title_and_body(lines)

        # Create section with proper robustness handling
        if not body:
            body = text.strip()
            
        sections = [
            ParsedSection(
                title=title,
                content=body,
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

        # Log for observability
        logger.info(f"Parsed text file '{filename}': {len(text)} characters, title='{title}'")
        
        # Create log entry for observability
        self._create_ingestion_log(filename, len(sections), len(text), title)

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
