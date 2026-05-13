"""
API endpoints for export functionality.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Tuple
import logging
import re

from backend.export.registry import export_registry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["export"])


class ExportRequest(BaseModel):
    """Stable request body for paper export operations."""

    paper_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Paper data containing title, authors, sections, citations, and metadata.",
    )
    format: str = Field(..., description="Export format or extension, e.g. markdown, md, .tex, docx.")
    output_path: Optional[str] = Field(default=None, description="Optional server-side output path.")
    include_bibliography: bool = Field(default=True, description="Whether bibliography should be included.")


FORMAT_ALIASES = {
    "markdown": "markdown",
    "md": "markdown",
    ".md": "markdown",
    "latex": "latex",
    "tex": "latex",
    ".tex": "latex",
    "bibtex": "bibtex",
    "bib": "bibtex",
    ".bib": "bibtex",
    "docx": "docx",
    ".docx": "docx",
}


MEDIA_TYPES = {
    "markdown": "text/markdown; charset=utf-8",
    "latex": "application/x-latex; charset=utf-8",
    "bibtex": "application/x-bibtex; charset=utf-8",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _normalize_format(format_name: str) -> Tuple[str, str]:
    """Normalize user-supplied format names/extensions to registry names and extensions."""
    normalized_input = (format_name or "").strip().lower()
    normalized_format = FORMAT_ALIASES.get(normalized_input)
    if not normalized_format:
        raise ValueError(
            f"Unsupported export format '{format_name}'. "
            f"Supported formats: markdown, latex, bibtex, docx."
        )

    exporter = export_registry.get_exporter_for_format(normalized_format)
    if not exporter:
        raise ValueError(f"No exporter found for normalized format: {normalized_format}")

    return normalized_format, exporter.get_file_extension()


def _safe_citation_key(value: Any, fallback: str) -> str:
    """Create a BibTeX-safe, stable citation key."""
    raw = str(value or fallback).strip().lower()
    key = re.sub(r"[^a-z0-9_:-]+", "_", raw).strip("_")
    return key or fallback


def _normalize_citations(citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate citations while preserving first-seen order and stable keys."""
    normalized: List[Dict[str, Any]] = []
    seen: set[str] = set()
    used_keys: set[str] = set()

    for citation in citations or []:
        if not isinstance(citation, dict):
            continue

        identity = str(
            citation.get("source_document_id")
            or citation.get("doi")
            or citation.get("key")
            or citation.get("id")
            or citation.get("title")
            or ""
        ).strip().lower()
        if not identity:
            identity = f"citation_{len(normalized) + 1}"

        if identity in seen:
            continue
        seen.add(identity)

        item = dict(citation)
        item.setdefault("id", f"cite_{len(normalized) + 1}")
        item.setdefault("entry_type", "article")
        item.setdefault("title", item.get("source_document", "Unknown Title"))
        item.setdefault("authors", [])
        item.setdefault("year", "Unknown")

        base_key = _safe_citation_key(
            item.get("key") or item.get("source_document_id") or item.get("title"),
            f"ref{len(normalized) + 1}",
        )
        key = base_key
        suffix = 2
        while key in used_keys:
            key = f"{base_key}_{suffix}"
            suffix += 1
        item["key"] = key
        used_keys.add(key)

        normalized.append(item)

    return normalized


def _normalize_paper_data(paper_data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a shallow-normalized paper payload with citation consistency preserved."""
    normalized = dict(paper_data or {})
    normalized["citations"] = _normalize_citations(normalized.get("citations", []))

    sections = []
    for section in normalized.get("sections", []) or []:
        if isinstance(section, dict):
            sections.append({
                "title": section.get("title", "Untitled Section"),
                "content": section.get("content", ""),
            })
    normalized["sections"] = sections

    return normalized


def _filename_for_export(paper_data: Dict[str, Any], extension: str) -> str:
    """Build a conservative filename for Content-Disposition."""
    title = str(paper_data.get("title") or "research-paper").strip().lower()
    stem = re.sub(r"[^a-z0-9]+", "-", title).strip("-") or "research-paper"
    return f"{stem}{extension}"


@router.post("/paper")
async def export_paper(request: ExportRequest) -> Response:
    """
    Export research paper data to specified format.
    
    Args:
        request: Stable JSON export request containing paper data, format, output path,
            and bibliography preference.
        
    Returns:
        Exported content as string
    """
    try:
        normalized_format, extension = _normalize_format(request.format)
        paper_data = _normalize_paper_data(request.paper_data)

        content = export_registry.export_to_format(
            paper_data=paper_data,
            format_name=normalized_format,
            output_path=request.output_path,
            include_bibliography=request.include_bibliography,
        )

        filename = _filename_for_export(paper_data, extension)
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Export-Format": normalized_format,
            "X-Export-Extension": extension,
        }

        response_content: str | bytes = content
        if normalized_format == "docx" and isinstance(content, str):
            # The current DOCX exporter emits a structured text representation.
            # Encode explicitly so the response is byte-safe for browser downloads
            # while retaining the canonical DOCX media type and extension.
            response_content = content.encode("utf-8")

        return Response(
            content=response_content,
            media_type=MEDIA_TYPES.get(normalized_format, "text/plain; charset=utf-8"),
            headers=headers,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
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
    try:
        normalized_format, extension = _normalize_format(format_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    exporter = export_registry.get_exporter_for_format(normalized_format)
    if not exporter:
        raise HTTPException(status_code=404, detail=f"Format {format_name} not found")
        
    return {
        "format": exporter.format_name,
        "normalized_format": normalized_format,
        "file_extension": extension,
        "media_type": MEDIA_TYPES.get(normalized_format, "text/plain; charset=utf-8"),
        "supported_formats": exporter.get_supported_formats(),
    }