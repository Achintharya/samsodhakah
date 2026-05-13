"""
LaTeX export — exports research papers in LaTeX format.
"""

from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.export.base import Exporter

logger = logging.getLogger(__name__)


class LaTeXExporter(Exporter):
    """
    Exports research papers in LaTeX format with proper citation handling.
    """

    def __init__(self) -> None:
        super().__init__("latex")

    def export(
        self,
        paper_data: Dict[str, Any],
        output_path: Optional[str] = None,
        include_bibliography: bool = True,
        document_class: str = "article",
        **kwargs
    ) -> str:
        """
        Export research paper data to LaTeX format.
        
        Args:
            paper_data: Dictionary containing paper data (sections, citations, etc.)
            output_path: Optional path to save the file
            include_bibliography: Whether to include bibliography section
            document_class: LaTeX document class (article, report, book, etc.)
            **kwargs: Additional format-specific parameters
            
        Returns:
            LaTeX content as string
        """
        # Document preamble
        content_parts = []
        content_parts.append(f"\\documentclass{{{document_class}}}")
        content_parts.append("")
        
        # Packages
        content_parts.append("% Packages")
        content_parts.append("\\usepackage[utf8]{inputenc}")
        content_parts.append("\\usepackage{geometry}")
        content_parts.append("\\usepackage{hyperref}")
        content_parts.append("\\usepackage{natbib}")
        content_parts.append("")
        
        # Document begin
        content_parts.append("\\begin{document}")
        content_parts.append("")
        
        # Title and metadata
        title = paper_data.get("title", "Untitled Research Paper")
        authors = paper_data.get("authors", [])
        abstract = paper_data.get("abstract", "")
        
        content_parts.append(f"\\title{{{title}}}")
        content_parts.append("")
        
        if authors:
            authors_str = ", ".join(authors)
            content_parts.append(f"\\author{{{authors_str}}}")
            content_parts.append("")
            
        content_parts.append("\\maketitle")
        content_parts.append("")
        
        if abstract:
            content_parts.append("\\begin{abstract}")
            content_parts.append(abstract)
            content_parts.append("\\end{abstract}")
            content_parts.append("")
        
        # Sections
        sections = paper_data.get("sections", [])
        for section in sections:
            section_title = section.get("title", "Untitled Section")
            section_content = section.get("content", "")
            
            # Escape LaTeX special characters in section title
            escaped_title = self._escape_latex(section_title)
            content_parts.append(f"\\section{{{escaped_title}}}")
            content_parts.append(section_content)
            content_parts.append("")
            
        # Bibliography
        if include_bibliography:
            citations = paper_data.get("citations", [])
            if citations:
                content_parts.append("\\bibliographystyle{plain}")
                content_parts.append("\\bibliography{references}")
                content_parts.append("")
        
        # Document end
        content_parts.append("\\end{document}")
        
        latex_content = "\n".join(content_parts)
        
        # Save if path provided
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(latex_content)
                logger.info(f"Saved LaTeX export to {output_path}")
            except Exception as e:
                logger.error(f"Failed to save LaTeX export: {e}")
                raise
        
        return latex_content

    def _escape_latex(self, text: str) -> str:
        """
        Escape special LaTeX characters in text.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        # Common LaTeX special characters
        replacements = {
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '^': '\\textasciicircum{}',
            '\\': '\\textbackslash{}',
            '<': '\\textless{}',
            '>': '\\textgreater{}',
        }
        
        escaped = text
        for char, replacement in replacements.items():
            escaped = escaped.replace(char, replacement)
            
        return escaped

    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats for this exporter."""
        return ["latex"]

    def get_file_extension(self) -> str:
        """Get file extension for this exporter."""
        return ".tex"


# Global instance
latex_exporter = LaTeXExporter()