"""
Async ingestion pipeline — orchestrates document parsing, section extraction,
semantic unit extraction, and indexing.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.config.settings import settings
from backend.ingestion.parsers.registry import parser_registry
from backend.ingestion.parsers.base import ParseResult
from backend.storage.local import local_storage
from backend.utils.token_metrics import token_metrics

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Orchestrates the full ingestion flow:

    1. Receive document bytes
    2. Parse into sections (via parser registry)
    3. Extract metadata
    4. Compute content hash
    5. Store document
    6. Queue for semantic extraction
    """

    async def ingest(
        self,
        filename: str,
        content: bytes,
        document_id: Optional[str] = None,
    ) -> dict:
        """
        Ingest a document into the system.

        Args:
            filename: Original filename (determines parser selection).
            content: Raw document bytes.
            document_id: Optional pre-assigned ID. Generated if not provided.

        Returns:
            Dictionary with ingestion results including document_id, sections, metadata.
        """
        import uuid
        doc_id = document_id or uuid.uuid4().hex[:12]

        logger.info(f"Starting ingestion for {filename} (id={doc_id})")

        # Step 1: Parse
        parse_result = parser_registry.parse(filename, content)
        if parse_result is None:
            return {
                "document_id": doc_id,
                "filename": filename,
                "status": "failed",
                "error": f"No parser available for {filename}",
            }

        # Step 2: Store raw document
        storage_meta = local_storage.upload_document(doc_id, filename, content)

        # Step 3: Build result
        result = {
            "document_id": doc_id,
            "filename": filename,
            "title": parse_result.title,
            "status": "parsed",
            "content_hash": parse_result.content_hash,
            "section_count": len(parse_result.sections),
            "file_size_bytes": len(content),
            "sections": [
                {
                    "title": s.title,
                    "level": s.level,
                    "order": s.order,
                    "content_length": len(s.content),
                    "content_hash": s.content_hash,
                }
                for s in parse_result.sections
            ],
            "metadata": parse_result.metadata,
            "storage_path": storage_meta.get("storage_path", ""),
            "created_at": datetime.now().isoformat(),
        }

        logger.info(
            f"Ingestion complete: {filename} → "
            f"{len(parse_result.sections)} sections, "
            f"{len(parse_result.raw_text)} chars"
        )

        # Track token metrics for ingestion
        token_metrics.log(
            operation="ingestion",
            subsystem="pipeline",
            input_tokens=len(content) // 4,  # rough estimate
            context_size_chars=len(content),
            compressed_size_chars=len(parse_result.raw_text),
            metadata={"filename": filename, "sections": len(parse_result.sections)},
        )

        return result

    async def ingest_from_url(
        self, url: str, document_id: Optional[str] = None
    ) -> dict:
        """
        Ingest content from a URL by fetching and parsing the HTML.

        Args:
            url: Web page URL.
            document_id: Optional pre-assigned ID.

        Returns:
            Ingestion result dictionary.
        """
        from backend.ingestion.extractors.html import html_extractor

        content = html_extractor.extract(url, max_chars=10000)
        if content is None:
            return {
                "status": "failed",
                "error": f"Failed to extract content from {url}",
            }

        # Treat extracted HTML as markdown for parsing purposes
        import uuid
        doc_id = document_id or uuid.uuid4().hex[:12]
        filename = f"web_{doc_id}.md"

        result = await self.ingest(filename, content.encode("utf-8"), doc_id)
        result["source_url"] = url
        return result


# Global pipeline instance
ingestion_pipeline = IngestionPipeline()