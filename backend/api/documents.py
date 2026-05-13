"""
Document management router — upload, list, retrieve, delete documents.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import Response

from backend.core.dependencies import get_storage, get_pipeline

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    storage=Depends(get_storage),
    pipeline=Depends(get_pipeline),
):
    """
    Upload and ingest a document (PDF, DOCX, MD, TXT, CSV).

    Returns ingestion results including document_id, sections, and metadata.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    result = await pipeline.ingest(file.filename, content)

    if result.get("status") == "failed":
        raise HTTPException(status_code=400, detail=result.get("error", "Ingestion failed"))

    return result


@router.get("")
async def list_documents(storage=Depends(get_storage)):
    """List all uploaded documents with metadata."""
    documents = storage.list_documents()
    return {
        "documents": documents,
        "total_count": len(documents),
    }


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    storage=Depends(get_storage),
):
    """Get document content by ID."""
    content = storage.get_document(document_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return Response(
        content=content,
        media_type="application/octet-stream",
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    storage=Depends(get_storage),
):
    """Delete a document by ID."""
    success = storage.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": f"Document {document_id} deleted"}