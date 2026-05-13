"""
Storage interface protocol.
Defines the contract for all storage backends.
"""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class StorageInterface(Protocol):
    """Protocol defining the storage operations contract."""

    def upload_document(self, document_id: str, filename: str, content: bytes) -> dict:
        """Store a document and return storage metadata."""
        ...

    def get_document(self, document_id: str) -> Optional[bytes]:
        """Retrieve document content by ID."""
        ...

    def delete_document(self, document_id: str) -> bool:
        """Remove a document from storage."""
        ...

    def list_documents(self) -> list[dict]:
        """List all stored documents with metadata."""
        ...

    def document_exists(self, document_id: str) -> bool:
        """Check if a document exists in storage."""
        ...