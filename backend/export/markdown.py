"""
Markdown export — exports research papers in Markdown format with citations.
"""

from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.export.base import Exporter

logger = logging.getLogger(__name__)


class MarkdownExporter(Exporter):
    """
    Exports research papers in Markdown format with proper citation handling.
    """

    def __init__(self) -> None:
        super().__init__("markdown")

    def export(
        self,
        paper_data: Dict[str, Any],
        output_path: Optional[str] = None,
        include_bibliography: bool = True,
    ) -> str:
        """
        Export research paper data to Markdown format.
        
        Args:
            paper_data: Dictionary containing paper data (sections, citations, etc.)
            output_path: Optional path to save the file
            include_bibliography: Whether to include bibliography section
            
        Returns:
            Markdown content as string
        """
        # Build the markdown content
        content_parts = []
        
        # Title and metadata
        title = paper_data.get("title", "Untitled Research Paper")
        authors = paper_data.get("authors", [])
        abstract = paper_data.get("abstract", "")
        
        content_parts.append(f"# {title}")
        content_parts.append("")
        
        if authors:
            authors_str = ", ".join(authors)
            content_parts.append(f"**Authors:** {authors_str}")
            content_parts.append("")
            
        if abstract:
            content_parts.append("**Abstract**")
            content_parts.append(abstract)
            content_parts.append("")
        
        # Sections
        sections = paper_data.get("sections", [])
        for section in sections:
            section_title = section.get("title", "Untitled Section")
            section_content = section.get("content", "")
            
            content_parts.append(f"## {section_title}")
            content_parts.append(section_content)
            content_parts.append("")
            
        # Bibliography
        if include_bibliography:
            citations = paper_data.get("citations", [])
            if citations:
                content_parts.append("---")
                content_parts.append("**References**")
                content_parts.append("")
                
                for i, citation in enumerate(citations, 1):
                    citation_str = self._format_citation(citation)
                    content_parts.append(f"{i}. {citation_str}")
                content_parts.append("")
        
        # Add timestamp
        content_parts.append("---")
        content_parts.append(f"_Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
        
        markdown_content = "\n".join(content_parts)
        
        # Save if path provided
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                logger.info(f"Saved markdown export to {output_path}")
            except Exception as e:
                logger.error(f"Failed to save markdown export: {e}")
                raise
        
        return markdown_content

    def _format_citation(self, citation: Dict[str, Any]) -> str:
        """
        Format a citation in Markdown style.
        
        Args:
            citation: Citation dictionary
            
        Returns:
            Formatted citation string
        """
        # Simplified citation formatting - in a real implementation,
        # this would handle different citation formats
        title = citation.get("title", "Unknown")
        authors = citation.get("authors", [])
        year = citation.get("year", "Unknown")
        
        authors_str = ", ".join(authors) if authors else "Unknown Author"
        return f"{authors_str} ({year}). {title}."

    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats for this exporter."""
        return ["markdown"]

    def get_file_extension(self) -> str:
        """Get file extension for this exporter."""
        return ".md"


# Global instance
markdown_exporter = MarkdownExporter()