"""
Base export interface for research paper exporters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class Exporter(ABC):
    """
    Abstract base class for all export formats.
    
    Defines the interface that all export formats must implement.
    """

    def __init__(self, format_name: str) -> None:
        self.format_name = format_name

    @abstractmethod
    def export(
        self,
        paper_data: Dict[str, Any],
        output_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Export paper data to the specific format.
        
        Args:
            paper_data: Dictionary containing paper data
            output_path: Optional path to save the file
            **kwargs: Additional format-specific parameters
            
        Returns:
            Exported content as string
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported export formats for this exporter.
        
        Returns:
            List of supported format strings
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """
        Get file extension for this exporter.
        
        Returns:
            File extension string (including the dot)
        """
        pass