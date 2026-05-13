"""
Lexical verification — exact and fuzzy string matching of claims against source documents.
"""

from __future__ import annotations

import re
import logging
import difflib

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class LexicalVerifier:
    """
    Verifies claims by matching their text against source documents
    using exact and fuzzy string matching.
    """

    def verify(
        self,
        claim: str,
        source_text: str,
        source_id: str,
    ) -> dict:
        """
        Verify a claim against a source text using lexical matching.

        Args:
            claim: The claim text to verify.
            source_text: The full source document text.
            source_id: Identifier for the source document.

        Returns:
            Dict with verification results.
        """
        claim_lower = claim.lower().strip()
        source_lower = source_text.lower()

        # Exact match (whole claim appears in source)
        exact_match = claim_lower in source_lower

        # Word overlap score
        claim_words = set(re.findall(r"\b\w+\b", claim_lower))
        source_words = set(re.findall(r"\b\w+\b", source_lower))

        # Remove stopwords for better precision
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
                     "for", "of", "with", "by", "is", "are", "was", "were", "be",
                     "been", "has", "have", "had", "do", "does", "did", "will",
                     "would", "can", "could", "may", "might", "shall", "should"}
        claim_content = claim_words - stopwords
        source_content = source_words - stopwords

        if not claim_content:
            return {
                "source_id": source_id,
                "claim": claim,
                "exact_match": exact_match,
                "word_overlap": 0.0,
                "max_fuzzy_ratio": 0.0,
                "verdict": "unverifiable",
                "confidence": 0.0,
            }

        overlap = len(claim_content & source_content) / len(claim_content)

        # Fuzzy matching on sentence level
        sentences = re.split(r'[.!?]+', source_text)
        max_fuzzy = 0.0
        best_match = ""

        for sentence in sentences:
            if len(sentence.strip()) < 10:
                continue
            ratio = difflib.SequenceMatcher(
                None, claim_lower, sentence.lower().strip()
            ).ratio()
            if ratio > max_fuzzy:
                max_fuzzy = ratio
                best_match = sentence.strip()

        # Determine verdict
        if exact_match or overlap >= 0.9:
            verdict = "supported"
            confidence = max(0.9, overlap)
        elif overlap >= 0.7 or max_fuzzy >= 0.8:
            verdict = "partially_supported"
            confidence = max(overlap, max_fuzzy)
        elif overlap >= 0.4:
            verdict = "weakly_supported"
            confidence = overlap
        else:
            verdict = "unsupported"
            confidence = overlap

        return {
            "source_id": source_id,
            "claim": claim,
            "exact_match": exact_match,
            "word_overlap": round(overlap, 4),
            "max_fuzzy_ratio": round(max_fuzzy, 4),
            "best_matching_sentence": best_match[:200] if best_match else "",
            "verdict": verdict,
            "confidence": round(confidence, 4),
        }


lexical_verifier = LexicalVerifier()