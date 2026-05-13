"""
Lightweight failure-analysis corpus for workflow hardening.

The corpus intentionally stays simple: JSONL records under runtime/data/evaluation.
It is meant for practical debugging and future evaluation harnesses, not as a
full experiment-tracking system.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.config.settings import settings

logger = logging.getLogger(__name__)


FAILURE_TYPES = {
    "poor_retrieval",
    "unsupported_claim",
    "contradictory_output",
    "weak_provenance",
    "malformed_export",
    "over_compressed_context",
    "token_overflow",
    "citation_mismatch",
}


class FailureCorpus:
    """Append-only JSONL store for workflow validation failures."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or settings.data_dir / "evaluation" / "failure_corpus.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        failure_type: str,
        summary: str,
        payload: Optional[Dict[str, Any]] = None,
        severity: str = "medium",
        source: str = "workflow",
    ) -> Dict[str, Any]:
        """Record a lightweight failure case and return the stored record."""
        normalized_type = failure_type if failure_type in FAILURE_TYPES else "unsupported_claim"
        record = {
            "id": f"failure_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "failure_type": normalized_type,
            "severity": severity,
            "source": source,
            "summary": summary,
            "payload": payload or {},
        }

        try:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        except Exception as exc:
            logger.warning("Failed to record failure corpus case: %s", exc)

        return record

    def list_cases(
        self,
        failure_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Read recent failure cases, newest first."""
        if not self.path.exists():
            return []

        cases: List[Dict[str, Any]] = []
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
            for line in reversed(lines):
                if not line.strip():
                    continue
                case = json.loads(line)
                if failure_type and case.get("failure_type") != failure_type:
                    continue
                cases.append(case)
                if len(cases) >= limit:
                    break
        except Exception as exc:
            logger.warning("Failed to read failure corpus: %s", exc)
        return cases

    def summary(self) -> Dict[str, Any]:
        """Return compact counts for workflow validation visibility."""
        cases = self.list_cases(limit=1000)
        counts: Dict[str, int] = {}
        for case in cases:
            kind = case.get("failure_type", "unknown")
            counts[kind] = counts.get(kind, 0) + 1
        return {
            "total_cases": len(cases),
            "counts_by_type": counts,
            "storage_path": str(self.path),
        }


failure_corpus = FailureCorpus()
