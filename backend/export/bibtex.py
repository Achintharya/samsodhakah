"""
BibTeX export — exports citations in BibTeX format.
"""

from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.export.base import Exporter

logger = logging.getLogger(__name__)


class BibTeXExporter(Exporter):
    """
    Exports citations in BibTeX format.
    """

    def __init__(self) -> None:
        super().__init__("bibtex")

    def export(
        self,
        paper_data: Dict[str, Any],
        output_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Export citations to BibTeX format.
        
        Args:
            paper_data: Dictionary containing paper data (especially citations)
            output_path: Optional path to save the file
            **kwargs: Additional format-specific parameters
            
        Returns:
            BibTeX content as string
        """
        citations = paper_data.get("citations", [])
        bibtex_entries = []
        
        for i, citation in enumerate(citations):
            entry = self._create_bibtex_entry(citation, i)
            if entry:
                bibtex_entries.append(entry)
        
        bibtex_content = "\n\n".join(bibtex_entries)
        
        # Save if path provided
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(bibtex_content)
                logger.info(f"Saved BibTeX export to {output_path}")
            except Exception as e:
                logger.error(f"Failed to save BibTeX export: {e}")
                raise
        
        return bibtex_content

    def _create_bibtex_entry(self, citation: Dict[str, Any], index: int) -> Optional[str]:
        """
        Create a BibTeX entry from citation data.
        
        Args:
            citation: Citation dictionary
            index: Entry index for auto-generated keys
            
        Returns:
            Formatted BibTeX entry string or None if invalid
        """
        # Required fields
        entry_type = citation.get("entry_type", "article")
        key = citation.get("key", f"ref{index}")
        
        # Extract fields
        title = citation.get("title", "Unknown Title")
        authors = citation.get("authors", [])
        year = citation.get("year", "Unknown")
        
        # Build BibTeX entry
        parts = []
        parts.append(f"@{entry_type}{{{key}")
        
        # Add title
        parts.append(f"  title = {{{title}}},")
        
        # Add authors
        if authors:
            authors_str = " and ".join(authors)
            parts.append(f"  author = {{{authors_str}}},")
        
        # Add year
        parts.append(f"  year = {{{year}}},")
        
        # Add other optional fields
        journal = citation.get("journal")
        if journal:
            parts.append(f"  journal = {{{journal}}},")
            
        volume = citation.get("volume")
        if volume:
            parts.append(f"  volume = {{{volume}}},")
            
        pages = citation.get("pages")
        if pages:
            parts.append(f"  pages = {{{pages}}},")
            
        doi = citation.get("doi")
        if doi:
            parts.append(f"  doi = {{{doi}}},")
            
        # Close entry
        parts.append("}")
        
        return "\n".join(parts)

    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats for this exporter."""
        return ["bibtex"]

    def get_file_extension(self) -> str:
        """Get file extension for this exporter."""
        return ".bib"


# Global instance
bibtex_exporter = BibTeXExporter()