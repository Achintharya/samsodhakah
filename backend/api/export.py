"""
API endpoints for export functionality.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response
from typing import Optional, List, Dict, Any
import logging

from backend.export.registry import export_registry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["export"])


@router.post("/paper")
async def export_paper(
    paper_data: Dict[str, Any],
    format: str,
    output_path: Optional[str] = None,
    include_bibliography: bool = True,
) -> Response:
    """
    Export research paper data to specified format.
    
    Args:
        paper_data: Dictionary containing paper data (sections, citations, etc.)
        format: Format to export to (markdown, latex, docx, bibtex)
        output_path: Optional path to save the file
        include_bibliography: Whether to include bibliography section
        
    Returns:
        Exported content as string
    """
    try:
        content = export_registry.export_to_format(
            paper_data=paper_data,
            format_name=format,
            output_path=output_path,
            include_bibliography=include_bibliography,
        )
        
        # Set appropriate content type based on format
        content_type = "text/plain"
        if format == "markdown":
            content_type = "text/markdown"
        elif format == "latex":
            content_type = "application/x-latex"
        elif format == "bibtex":
            content_type = "application/x-bibtex"
        elif format == "docx":
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        return Response(content=content, media_type=content_type)
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/formats")
async def get_available_formats() -> List[str]:
    """
    Get list of available export formats.
    
    Returns:
        List of available format names
    """
    return export_registry.get_available_formats()


@router.get("/format-info/{format_name}")
async def get_format_info(format_name: str) -> Dict[str, Any]:
    """
    Get information about a specific export format.
    
    Args:
        format_name: Name of the format to get information about
        
    Returns:
        Format information including file extension
    """
    exporter = export_registry.get_exporter_for_format(format_name)
    if not exporter:
        raise HTTPException(status_code=404, detail=f"Format {format_name} not found")
        
    return {
        "format": exporter.format_name,
        "file_extension": exporter.get_file_extension(),
        "supported_formats": exporter.get_supported_formats(),
    }