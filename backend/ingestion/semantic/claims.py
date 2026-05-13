"""
Claim extraction — identifies and extracts claims from text using pattern matching.
"""

from __future__ import annotations

import re
import logging

logger = logging.getLogger(__name__)

# Patterns that often introduce scientific claims
CLAIM_PATTERNS = [
    r"(?:we|our|the)\s+(?:show|demonstrate|find|report|propose|argue|conclude|suggest|indicate|reveal|establish|provide evidence)\s+that\b",
    r"(?:these|our)\s+(?:results|findings|data|observations|experiments|analyses)\s+(?:show|demonstrate|indicate|suggest|reveal|support|confirm|provide evidence)\b",
    r"(?:this|our)\s+(?:study|work|paper|analysis|experiment|investigation)\s+(?:shows|demonstrates|indicates|suggests|reveals|provides|confirms|establishes)\b",
    r"\b(?:significantly|substantially|dramatically|notably|importantly)\b",
    r"\b(?:we conclude|we hypothesize|we propose|we argue|we find)\b",
    r"\bI\s+(?:show|demonstrate|find|report|propose|argue|conclude|suggest)\s+that\b",
    r"\bin this paper,?\s+(?:we|the author)\b",
    r"\b(?:our approach|our method|our framework|our model|our system)\s+(?:achieves|outperforms|improves|reduces|increases|provides|enables)\b",
]

# Compile patterns
COMPILED_CLAIM_PATTERNS = [re.compile(p, re.IGNORECASE) for p in CLAIM_PATTERNS]


def extract_claims(text: str) -> list[dict]:
    """
    Extract potential claims from text using pattern matching.

    Args:
        text: The text to extract claims from.

    Returns:
        List of dicts with 'text' and 'confidence' keys.
    """
    claims = []
    seen = set()

    for pattern in COMPILED_CLAIM_PATTERNS:
        for match in pattern.finditer(text):
            # Extract the sentence containing the match
            start = text.rfind(".", 0, match.start()) + 1
            if start == 0:
                start = 0
            end = text.find(".", match.end())
            if end == -1:
                end = len(text)
            end += 1  # Include the period

            sentence = text[start:end].strip()
            if not sentence or sentence in seen:
                continue
            seen.add(sentence)

            # Skip short fragments
            if len(sentence) < 20:
                continue

            # Calculate a simple confidence based on pattern specificity
            pattern_length = len(match.group())
            confidence = min(0.5 + (pattern_length / 200), 0.95)

            claims.append({
                "text": sentence,
                "confidence": round(confidence, 3),
                "pattern_matched": match.group()[:50],
            })

    logger.info(f"Extracted {len(claims)} claims from {len(text)} chars")
    return claims