"""
Local filesystem storage backend.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from datetime import datetime
import logging

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class LocalStorage:
    """Local filesystem storage for documents and artifacts."""

    def __init__(self, root_path: Optional[Path] = None) -> None:
        self.root = root_path or settings.storage_root
        self.documents_dir = self.root / "documents"
        self.exports_dir = self.root / "exports"
        self.cache_dir = settings.cache_dir

        for directory in [self.documents_dir, self.exports_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"LocalStorage initialized at: {self.root}")

    # ── Document operations ──────────────────────────────────────

    def upload_document(self, document_id: str, filename: str, content: bytes) -> dict:
        """Store a document file."""
        file_path = self._document_path(document_id, filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(content)

        metadata = {
            "document_id": document_id,
            "filename": filename,
            "storage_path": str(file_path),
            "size_bytes": len(content),
            "created_at": datetime.now().isoformat(),
        }

        # Write metadata alongside the file
        meta_path = file_path.with_suffix(".json")
        if not meta_path.exists():
            import json
            meta_path.write_text(json.dumps(metadata, indent=2))

        logger.info(f"Stored document {document_id} as {filename}")
        return metadata

    def get_document(self, document_id: str, filename: Optional[str] = None) -> Optional[bytes]:
        """Retrieve document content by ID."""
        file_path = self._find_document(document_id, filename)
        if file_path and file_path.exists():
            return file_path.read_bytes()
        return None

    def delete_document(self, document_id: str, filename: Optional[str] = None) -> bool:
        """Remove a document from storage."""
        file_path = self._find_document(document_id, filename)
        if file_path and file_path.exists():
            file_path.unlink()
            # Also remove metadata file
            meta_path = file_path.with_suffix(".json")
            if meta_path.exists():
                meta_path.unlink()
            logger.info(f"Deleted document {document_id}")
            return True
        return False

    def list_documents(self) -> list[dict]:
        """List all stored documents with metadata."""
        documents = []
        for doc_dir in self.documents_dir.iterdir():
            if doc_dir.is_dir():
                for file_path in doc_dir.iterdir():
                    if file_path.suffix in (".pdf", ".docx", ".md", ".txt", ".csv"):
                        meta_path = file_path.with_suffix(".json")
                        if meta_path.exists():
                            import json
                            metadata = json.loads(meta_path.read_text())
                            documents.append(metadata)
                        else:
                            stat = file_path.stat()
                            documents.append({
                                "document_id": doc_dir.name,
                                "filename": file_path.name,
                                "storage_path": str(file_path),
                                "size_bytes": stat.st_size,
                                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            })
        return sorted(documents, key=lambda d: d.get("created_at", ""), reverse=True)

    def document_exists(self, document_id: str) -> bool:
        """Check if a document exists in storage."""
        doc_dir = self.documents_dir / document_id
        return doc_dir.exists() and any(doc_dir.iterdir())

    # ── Export operations ─────────────────────────────────────────

    def save_export(self, filename: str, content: str | bytes) -> Path:
        """Save an exported file (markdown, docx, latex, etc.)."""
        file_path = self.exports_dir / filename
        if isinstance(content, str):
            file_path.write_text(content, encoding="utf-8")
        else:
            file_path.write_bytes(content)
        logger.info(f"Saved export: {filename}")
        return file_path

    # ── Private helpers ───────────────────────────────────────────

    def _document_path(self, document_id: str, filename: str) -> Path:
        return self.documents_dir / document_id / filename

    def _find_document(self, document_id: str, filename: Optional[str] = None) -> Optional[Path]:
        doc_dir = self.documents_dir / document_id
        if not doc_dir.exists():
            return None
        if filename:
            return doc_dir / filename
        # Return first file in the directory
        for f in doc_dir.iterdir():
            if f.is_file() and f.suffix in (".pdf", ".docx", ".md", ".txt", ".csv"):
                return f
        return None


# Global singleton
local_storage = LocalStorage()