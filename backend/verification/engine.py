"""
Verification engine — multi-stage orchestrator for claim verification.

Pipeline:
1. Lexical verification (exact + fuzzy matching)
2. Numerical verification (value comparison)
3. Consensus assessment
4. Contradiction detection
"""

from __future__ import annotations

import logging
from typing import Optional

from backend.verification.lexical import lexical_verifier
from backend.verification.numerical import numerical_verifier
from backend.utils.token_metrics import token_metrics

logger = logging.getLogger(__name__)


class VerificationEngine:
    """
    Orchestrates multi-stage verification of claims against source documents.

    Every verification produces:
    - supporting evidence with provenance
    - contradictions (if any)
    - confidence score
    """

    async def verify_claim(
        self,
        claim: str,
        source_texts: dict[str, str],  # source_id -> source_text
    ) -> dict:
        """
        Verify a single claim against multiple source documents.

        Args:
            claim: The claim text to verify.
            source_texts: Mapping of source_id to source document text.

        Returns:
            Consolidated verification result.
        """
        if not source_texts:
            return {
                "claim": claim,
                "verdict": "unverifiable",
                "confidence": 0.0,
                "evidence_count": 0,
                "details": "No source documents provided",
            }

        results = []

        for source_id, source_text in source_texts.items():
            # Stage 1: Lexical verification
            lexical_result = lexical_verifier.verify(claim, source_text, source_id)

            # Stage 2: Numerical verification (if applicable)
            numerical_result = numerical_verifier.verify(claim, source_text, source_id)

            combined_confidence = self._combine_confidence(
                lexical_result["confidence"],
                numerical_result.get("confidence", 0.0),
            )

            results.append({
                "source_id": source_id,
                "lexical": lexical_result,
                "numerical": numerical_result,
                "combined_confidence": combined_confidence,
            })

        # Consensus across sources
        confidences = [r["combined_confidence"] for r in results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Check for contradictions across sources
        contradictions = self._detect_contradictions(results)

        # Determine overall verdict
        if avg_confidence >= 0.8:
            overall_verdict = "supported"
        elif avg_confidence >= 0.5:
            overall_verdict = "partially_supported"
        elif contradictions:
            overall_verdict = "contradicted"
        else:
            overall_verdict = "unsupported"

        result = {
            "claim": claim,
            "verdict": overall_verdict,
            "confidence": round(avg_confidence, 4),
            "source_results": results,
            "contradictions": contradictions,
            "evidence_count": len(results),
            "supported_count": sum(1 for r in results if r["combined_confidence"] >= 0.7),
            "contradicted_count": len(contradictions),
        }

        # Track token metrics
        total_source_chars = sum(len(t) for t in source_texts.values())
        token_metrics.log(
            operation="verification",
            subsystem="engine",
            input_tokens=len(claim) // 4 + total_source_chars // 4,
            context_size_chars=total_source_chars,
            metadata={
                "sources": len(source_texts),
                "verdict": overall_verdict,
                "confidence": avg_confidence,
            },
        )

        return result

    def verify_batch(
        self,
        claims: list[str],
        source_texts: dict[str, str],
    ) -> list[dict]:
        """Verify multiple claims against the same source texts."""
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            results = [
                loop.run_until_complete(self.verify_claim(claim, source_texts))
                for claim in claims
            ]
        finally:
            loop.close()
        return results

    def _combine_confidence(
        self,
        lexical_conf: float,
        numerical_conf: float,
    ) -> float:
        """Combine confidence scores from different verification methods."""
        # Numerical verification weights higher when available
        if numerical_conf > 0:
            return 0.4 * lexical_conf + 0.6 * numerical_conf
        return lexical_conf

    def _detect_contradictions(self, results: list[dict]) -> list[dict]:
        """Detect contradictions across different sources."""
        contradictions = []

        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                r1 = results[i]
                r2 = results[j]

                # Check numerical contradictions
                n1 = r1.get("numerical", {})
                n2 = r2.get("numerical", {})
                if n1.get("has_numerical_claim") and n2.get("has_numerical_claim"):
                    for comp1 in n1.get("comparisons", []):
                        for comp2 in n2.get("comparisons", []):
                            if (
                                comp1.get("unit") == comp2.get("unit")
                                and comp1.get("match") != comp2.get("match")
                            ):
                                contradictions.append({
                                    "type": "numerical",
                                    "source_a": r1["source_id"],
                                    "source_b": r2["source_id"],
                                    "detail": (
                                        f"Source A says {comp1.get('claim_value')} "
                                        f"(match={comp1.get('match')}) vs "
                                        f"Source B says {comp2.get('claim_value')} "
                                        f"(match={comp2.get('match')})"
                                    ),
                                    "severity": 0.7,
                                })

                # Check lexical contradictions
                l1 = r1.get("lexical", {})
                l2 = r2.get("lexical", {})
                if (
                    l1.get("verdict") in ("supported", "partially_supported")
                    and l2.get("verdict") in ("unsupported", "weakly_supported")
                ):
                    contradictions.append({
                        "type": "lexical",
                        "source_a": r1["source_id"],
                        "source_b": r2["source_id"],
                        "detail": (
                            f"Source A supports claim ({l1.get('confidence')}), "
                            f"Source B does not ({l2.get('confidence')})"
                        ),
                        "severity": 0.5,
                    })

        return contradictions


# Global instance
verification_engine = VerificationEngine()