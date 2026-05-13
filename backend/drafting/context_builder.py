"""
PromptContextBuilder — token-budgeted, compressed context construction for LLM drafting.

This is the single most critical module for token optimization.
It enforces that NO raw documents, excessive contexts, or unprioritized evidence
ever reaches an LLM call.
"""

from __future__ import annotations

import logging
from typing import Optional

from backend.config.settings import settings
from backend.evaluation.failure_corpus import failure_corpus
from backend.utils.token_metrics import token_metrics

logger = logging.getLogger(__name__)


class PromptContextBuilder:
    """
    Builds minimal, token-budgeted prompt contexts for LLM drafting.

    Responsibilities:
    - Token budgeting per section
    - Semantic compression (redundancy removal)
    - Evidence prioritization by confidence
    - Contradiction highlighting
    - Citation linking preparation
    """

    # Rough estimate: 1 token ≈ 4 characters for English text
    CHARS_PER_TOKEN = 4

    def __init__(self) -> None:
        self.max_tokens = settings.max_draft_tokens
        self.compression_ratio = settings.compression_target_ratio

    def build_context(
        self,
        topic: str,
        evidence_units: list[dict],
        semantic_units: list[dict],
        verification_results: Optional[list[dict]] = None,
    ) -> dict:
        """
        Build a compressed, token-budgeted context for drafting.

        Args:
            topic: The drafting topic/query.
            evidence_units: List of evidence dicts with 'content', 'confidence', 'role'.
            semantic_units: List of semantic units with 'content', 'type', 'confidence'.
            verification_results: Optional list of verification result dicts.

        Returns:
            Dict with 'context' (compressed text), 'token_count', 'compression_stats'.
        """
        # Phase 1: Collect and sort all evidence
        all_items = []

        # Add evidence units
        for ev in evidence_units:
            content = (ev.get("content", "") or "").strip()
            if len(content) < 40:
                continue
            all_items.append({
                "content": content[:900],
                "confidence": ev.get("confidence", 0.0),
                "role": ev.get("role", "neutral"),
                "type": "evidence",
                "source": ev.get("source_document_id") or ev.get("source_id", ""),
                "evidence_id": ev.get("id"),
            })

        # Add semantic units
        for su in semantic_units:
            unit_type = su.get("unit_type", "unknown")
            # Only include high-value types
            if unit_type in ("claim", "methodology", "experimental_result", "metric"):
                content = (su.get("content", "") or "").strip()
                if len(content) < 40:
                    continue
                all_items.append({
                    "content": content[:700],
                    "confidence": su.get("confidence", 1.0) * 0.8,  # slightly discount semantic extraction
                    "role": "semantic",
                    "type": unit_type,
                    "source": su.get("document_id", ""),
                    "semantic_unit_id": su.get("id"),
                })

        # Phase 2: Deduplicate by content similarity
        deduplicated = self._deduplicate(all_items)

        # Phase 3: Sort by confidence descending
        deduplicated.sort(key=lambda x: x["confidence"], reverse=True)
        deduplicated = self._balance_sources(deduplicated)

        # Phase 4: Calculate token budget
        topic_chars = len(topic)
        topic_tokens = topic_chars // self.CHARS_PER_TOKEN
        remaining_budget = self.max_tokens - topic_tokens

        # Reserve tokens for system prompt and formatting overhead (~200 tokens)
        overhead_tokens = 200
        remaining_budget -= overhead_tokens

        if remaining_budget < 100:
            remaining_budget = 100

        max_evidence_chars = remaining_budget * self.CHARS_PER_TOKEN

        # Phase 5: Build compressed context
        context_parts = []
        total_chars = 0

        # Add contradictions first (highest priority signal)
        contradictions = []
        if verification_results:
            for vr in verification_results:
                for c in vr.get("contradictions", []):
                    contradictions.append(c)

        if contradictions:
            contradiction_text = "\n".join(
                f"⚠ CONTRADICTION: {c.get('detail', '')}" for c in contradictions[:3]
            )
            context_parts.append(contradiction_text)
            total_chars += len(contradiction_text)

        # Add evidence items within budget
        for item in deduplicated:
            item_chars = len(item["content"]) + 50  # +50 for formatting
            if total_chars + item_chars > max_evidence_chars:
                break

            prefix = self._get_item_prefix(item)
            source = item.get("source") or "unknown-source"
            identifier = item.get("evidence_id") or item.get("semantic_unit_id") or "untracked"
            context_parts.append(f"{prefix}[source={source}; id={identifier}] {item['content']}")
            total_chars += item_chars

        compressed_context = "\n\n".join(context_parts)

        # Phase 6: Calculate stats
        original_chars = sum(len(i["content"]) for i in all_items)
        compression_stats = {
            "original_items": len(all_items),
            "after_deduplication": len(deduplicated),
            "included_items": len(context_parts),
            "original_chars": original_chars,
            "compressed_chars": total_chars,
            "compression_ratio": round(1.0 - (total_chars / max(original_chars, 1)), 4),
            "topic_tokens": topic_tokens,
            "evidence_tokens": total_chars // self.CHARS_PER_TOKEN,
            "total_tokens": topic_tokens + (total_chars // self.CHARS_PER_TOKEN) + overhead_tokens,
            "budget_utilization": round(
                (total_chars / self.CHARS_PER_TOKEN) / remaining_budget * 100, 1
            ),
        }

        # Track token metrics
        token_metrics.log(
            operation="draft_section",
            subsystem="context_builder",
            input_tokens=original_chars // self.CHARS_PER_TOKEN,
            context_size_chars=original_chars,
            compressed_size_chars=total_chars,
            compression_ratio=compression_stats["compression_ratio"],
            metadata={
                "original_items": len(all_items),
                "included_items": len(context_parts),
                "max_tokens": self.max_tokens,
            },
        )

        logger.info(
            f"Context built: {len(context_parts)} items from {len(all_items)} "
            f"({compression_stats['compression_ratio']:.1%} compression)"
        )

        if all_items and compression_stats["included_items"] <= 1:
            failure_corpus.record(
                "over_compressed_context",
                "PromptContextBuilder included one or fewer evidence items despite available context.",
                {"topic": topic, "compression_stats": compression_stats},
                severity="medium",
                source="context_builder",
            )
        if compression_stats["total_tokens"] > self.max_tokens:
            failure_corpus.record(
                "token_overflow",
                "PromptContextBuilder context exceeded configured draft token budget.",
                {"topic": topic, "compression_stats": compression_stats},
                severity="high",
                source="context_builder",
            )

        return {
            "context": compressed_context,
            "token_count": compression_stats["total_tokens"],
            "compression_stats": compression_stats,
        }

    def _deduplicate(self, items: list[dict]) -> list[dict]:
        """Remove near-duplicate content items."""
        seen = set()
        unique = []

        for item in items:
            # Use content prefix as fingerprint for dedup
            content = item.get("content", "").strip().lower()
            fingerprint = content[:100]  # first ~100 chars as fingerprint

            if fingerprint in seen:
                continue
            seen.add(fingerprint)

            # Update confidence to max if duplicate by different sources
            existing = next(
                (u for u in unique if u.get("_fingerprint") == fingerprint), None
            )
            if existing:
                existing["confidence"] = max(existing["confidence"], item["confidence"])
                continue

            item["_fingerprint"] = fingerprint
            unique.append(item)

        return unique

    def _balance_sources(self, items: list[dict]) -> list[dict]:
        """Avoid overloading the context with many near-neighbor items from one source."""
        balanced = []
        source_counts: dict[str, int] = {}
        deferred = []
        for item in items:
            source = item.get("source") or "unknown"
            if source_counts.get(source, 0) < 4:
                balanced.append(item)
                source_counts[source] = source_counts.get(source, 0) + 1
            else:
                deferred.append(item)
        return balanced + deferred

    def _get_item_prefix(self, item: dict) -> str:
        """Get a short prefix label for an evidence item."""
        role = item.get("role", "")
        unit_type = item.get("type", "information")

        if role == "supports":
            return "✓ EVIDENCE: "
        elif role == "contradicts":
            return "✗ CONTRADICTS: "
        elif role == "semantic":
            type_labels = {
                "claim": "→ CLAIM: ",
                "methodology": "→ METHOD: ",
                "experimental_result": "→ RESULT: ",
                "metric": "→ METRIC: ",
            }
            return type_labels.get(unit_type, "→ NOTE: ")
        else:
            return "• "


# Global instance
context_builder = PromptContextBuilder()