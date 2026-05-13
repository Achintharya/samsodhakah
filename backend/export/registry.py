"""
Export registry — manages available export formats and their registration.
"""

from __future__ import annotations

from typing import Optional, Dict, List
from pathlib import Path

from backend.export.base import Exporter
from backend.export.markdown import markdown_exporter
from backend.export.bibtex import bibtex_exporter
from backend.export.latex import latex_exporter
from backend.export.docx import docx_exporter


class ExportRegistry:
    """
    Registry for managing available export formats.
    
    Provides a centralized way to discover and use different export formats.
    """

    def __init__(self) -> None:
        self._exporters: Dict[str, Exporter] = {}
        self._registered_exporters = [
            markdown_exporter,
            bibtex_exporter,
            latex_exporter,
            docx_exporter,
        ]
        self._initialize_registry()

    def _initialize_registry(self) -> None:
        """Initialize the registry with all available exporters."""
        for exporter in self._registered_exporters:
            self.register_exporter(exporter)

    def register_exporter(self, exporter: Exporter) -> None:
        """
        Register an exporter with the registry.
        
        Args:
            exporter: Exporter instance to register
        """
        self._exporters[exporter.format_name] = exporter
        # Register all supported formats
        for format_name in exporter.get_supported_formats():
            self._exporters[format_name] = exporter

    def get_exporter(self, format_name: str) -> Optional[Exporter]:
        """
        Get an exporter by format name.
        
        Args:
            format_name: Name of the format to get exporter for
            
        Returns:
            Exporter instance or None if not found
        """
        return self._exporters.get(format_name)

    def get_available_formats(self) -> List[str]:
        """
        Get list of all available export formats.
        
        Returns:
            List of available format names
        """
        return list(self._exporters.keys())

    def get_exporter_for_format(self, format_name: str) -> Optional[Exporter]:
        """
        Get exporter specifically for a format (handles aliases).
        
        Args:
            format_name: Format name to find exporter for
            
        Returns:
            Exporter instance for format or None
        """
        # Try to find exact match first
        exporter = self.get_exporter(format_name)
        if exporter:
            return exporter
            
        # Try to find by file extension
        for fmt, exp in self._exporters.items():
            if exp.get_file_extension() == format_name:
                return exp
                
        return None

    def export_to_format(
        self,
        paper_data: Dict,
        format_name: str,
        output_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Export paper data to a specific format.
        
        Args:
            paper_data: Dictionary containing paper data
            format_name: Format to export to
            output_path: Optional path to save the file
            **kwargs: Additional parameters for export
            
        Returns:
            Exported content as string
        """
        exporter = self.get_exporter(format_name)
        if not exporter:
            raise ValueError(f"No exporter found for format: {format_name}")
            
        return exporter.export(paper_data, output_path, **kwargs)

    def get_file_extension(self, format_name: str) -> str:
        """
        Get the file extension for a specific format.
        
        Args:
            format_name: Format name
            
        Returns:
            File extension string
        """
        exporter = self.get_exporter(format_name)
        if exporter:
            return exporter.get_file_extension()
        return ".dat"  # Default fallback


# Global registry instance
export_registry = ExportRegistry()