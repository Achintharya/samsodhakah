"""
Semantic memory — central store for documents, sections, semantic units, and evidence.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class SemanticMemory:
    """
    In-memory semantic store with persistence to JSON files.

    Stores:
    - Documents with metadata
    - Sections with content
    - Semantic units with embeddings
    - Evidence units with verification results
    """

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self.storage_path = storage_path or settings.data_dir / "semantic_memory"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # In-memory stores
        self.documents: dict[str, dict] = {}
        self.sections: dict[str, dict] = {}
        self.semantic_units: dict[str, dict] = {}
        self.evidence_units: dict[str, dict] = {}
        self.claims: dict[str, dict] = {}
        self.citations: dict[str, dict] = {}

        # Load persisted data
        self._load_all()

    # ── Document operations ──────────────────────────────────────

    def add_document(self, document: dict) -> str:
        """Add or update a document in memory."""
        doc_id = document["document_id"]
        document["_updated_at"] = datetime.now().isoformat()
        self.documents[doc_id] = document
        self._save("documents")
        return doc_id

    def get_document(self, document_id: str) -> Optional[dict]:
        return self.documents.get(document_id)

    def list_documents(self) -> list[dict]:
        return sorted(
            self.documents.values(),
            key=lambda d: d.get("created_at", ""),
            reverse=True,
        )

    def delete_document(self, document_id: str) -> bool:
        if document_id in self.documents:
            del self.documents[document_id]
            # Also remove associated sections and semantic units
            self.sections = {
                k: v for k, v in self.sections.items()
                if v.get("document_id") != document_id
            }
            self.semantic_units = {
                k: v for k, v in self.semantic_units.items()
                if v.get("document_id") != document_id
            }
            self._save_all()
            return True
        return False

    # ── Section operations ─────────────────────────────────────────

    def add_section(self, section: dict) -> str:
        section_id = section.get("id", section.get("title", ""))
        section["_updated_at"] = datetime.now().isoformat()
        self.sections[section_id] = section
        self._save("sections")
        return section_id

    def add_sections(self, sections: list[dict]) -> None:
        for section in sections:
            self.add_section(section)

    def get_document_sections(self, document_id: str) -> list[dict]:
        return [
            s for s in self.sections.values()
            if s.get("document_id") == document_id
        ]

    # ── Semantic Unit operations ─────────────────────────────────

    def add_semantic_unit(self, unit: dict) -> str:
        unit_id = unit.get("id", f"su_{len(self.semantic_units)}")
        unit["_updated_at"] = datetime.now().isoformat()
        self.semantic_units[unit_id] = unit
        self._save("semantic_units")
        return unit_id

    def add_semantic_units(self, units: list[dict]) -> None:
        for unit in units:
            self.add_semantic_unit(unit)

    def get_document_semantic_units(self, document_id: str) -> list[dict]:
        return [
            u for u in self.semantic_units.values()
            if u.get("document_id") == document_id
        ]

    def get_units_by_type(self, unit_type: str) -> list[dict]:
        return [
            u for u in self.semantic_units.values()
            if u.get("unit_type") == unit_type
        ]

    # ── Evidence operations ──────────────────────────────────────

    def add_evidence_unit(self, evidence: dict) -> str:
        ev_id = evidence.get("id", f"ev_{len(self.evidence_units)}")
        evidence["_updated_at"] = datetime.now().isoformat()
        self.evidence_units[ev_id] = evidence
        self._save("evidence_units")
        return ev_id

    def get_evidence_for_claim(self, claim_id: str) -> list[dict]:
        return [
            e for e in self.evidence_units.values()
            if e.get("claim_id") == claim_id
        ]

    def get_evidence_for_document(self, document_id: str) -> list[dict]:
        return [
            e for e in self.evidence_units.values()
            if e.get("source_document_id") == document_id
        ]

    # ── Claim operations ─────────────────────────────────────────

    def add_claim(self, claim: dict) -> str:
        claim_id = claim.get("id", f"cl_{len(self.claims)}")
        claim["_updated_at"] = datetime.now().isoformat()
        self.claims[claim_id] = claim
        self._save("claims")
        return claim_id

    def get_all_claims(self) -> list[dict]:
        return list(self.claims.values())

    # ── Citation operations ──────────────────────────────────────

    def add_citation(self, citation: dict) -> str:
        cit_id = citation.get("id", f"ct_{len(self.citations)}")
        citation["_updated_at"] = datetime.now().isoformat()
        self.citations[cit_id] = citation
        self._save("citations")
        return cit_id

    def get_document_citations(self, document_id: str) -> list[dict]:
        return [
            c for c in self.citations.values()
            if c.get("document_id") == document_id
        ]

    # ── Retrieval helpers ────────────────────────────────────────

    def get_all_texts_for_indexing(self) -> list[dict]:
        """Get all text content for building the retrieval index."""
        texts = []
        for doc in self.documents.values():
            texts.append({
                "id": doc["document_id"],
                "text": doc.get("title", "") + "\n" + doc.get("filename", ""),
                "metadata": {"type": "document", "filename": doc.get("filename")},
            })
        for section in self.sections.values():
            texts.append({
                "id": section.get("id", ""),
                "text": section.get("title", "") + "\n" + section.get("content", ""),
                "metadata": {
                    "type": "section",
                    "document_id": section.get("document_id"),
                },
            })
        for unit in self.semantic_units.values():
            texts.append({
                "id": unit.get("id", ""),
                "text": unit.get("content", ""),
                "metadata": {
                    "type": unit.get("unit_type", "semantic_unit"),
                    "document_id": unit.get("document_id"),
                },
            })
        for evidence in self.evidence_units.values():
            texts.append({
                "id": evidence.get("id", ""),
                "text": evidence.get("content", ""),
                "metadata": {
                    "type": "evidence_unit",
                    "document_id": evidence.get("source_document_id"),
                    "section_id": evidence.get("source_section_id"),
                    "semantic_unit_id": evidence.get("source_semantic_unit_id"),
                    "role": evidence.get("role", "neutral"),
                    "confidence": evidence.get("confidence", 0.0),
                },
            })
        return texts

    # ── Persistence ─────────────────────────────────────────────

    def _save(self, store_name: str) -> None:
        """Persist a single store to JSON."""
        store_map = {
            "documents": self.documents,
            "sections": self.sections,
            "semantic_units": self.semantic_units,
            "evidence_units": self.evidence_units,
            "claims": self.claims,
            "citations": self.citations,
        }
        store = store_map.get(store_name)
        if store is not None:
            path = self.storage_path / f"{store_name}.json"
            try:
                path.write_text(
                    json.dumps(store, indent=2, default=str),
                    encoding="utf-8",
                )
            except Exception as e:
                logger.warning(f"Failed to persist {store_name}: {e}")

    def _save_all(self) -> None:
        """Persist all stores."""
        for store_name in ["documents", "sections", "semantic_units",
                           "evidence_units", "claims", "citations"]:
            self._save(store_name)

    def _load_all(self) -> None:
        """Load all stores from disk."""
        store_map = {
            "documents.json": self.documents,
            "sections.json": self.sections,
            "semantic_units.json": self.semantic_units,
            "evidence_units.json": self.evidence_units,
            "claims.json": self.claims,
            "citations.json": self.citations,
        }
        for filename, store in store_map.items():
            path = self.storage_path / filename
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    store.update(data)
                    logger.debug(f"Loaded {len(data)} {filename.replace('.json', '')}")
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")


# Global instance
semantic_memory = SemanticMemory()