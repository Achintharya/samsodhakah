"""
Keyphrase extraction — extracts important phrases from text using TF-IDF-like scoring.
No external dependencies beyond standard library for basic version.
"""

from __future__ import annotations

import re
import logging
from collections import Counter
from typing import Optional

logger = logging.getLogger(__name__)

# Common English stopwords
STOPWORDS = set(
    "a an the and or but in on at to for of with by from as is are was were "
    "be been being have has had do does did will would shall should may might "
    "can could must need ought dare used about above across after against "
    "along among around at before behind below beneath beside between beyond "
    "down during except for from in inside into near of off on out outside "
    "over through throughout to toward under underneath until up upon with "
    "within without".split()
)

# Scientific section headers to ignore
SECTION_HEADERS = {
    "introduction", "methodology", "methods", "results", "discussion",
    "conclusion", "references", "abstract", "background", "related work",
    "experimental setup", "experiments", "evaluation", "conclusions",
    "future work", "limitations", "acknowledgments", "appendix",
}

# Technical term patterns
TECHNICAL_PATTERN = re.compile(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b")  # CamelCase
ACRONYM_PATTERN = re.compile(r"\b[A-Z]{2,}\b")  # All-caps acronyms
NUMBERED_TERM = re.compile(r"\b[A-Za-z]+-\d+\b")  # Model names like BERT-3


def extract_keyphrases(
    text: str,
    max_phrases: int = 20,
    min_length: int = 2,
    max_length: int = 4,
) -> list[dict]:
    """
    Extract keyphrases from text using frequency and position scoring.

    Args:
        text: Text to analyze.
        max_phrases: Maximum number of phrases to return.
        min_length: Minimum words per phrase.
        max_length: Maximum words per phrase.

    Returns:
        List of dicts with 'text' and 'score' keys, sorted by score descending.
    """
    # Clean text
    text_lower = text.lower()
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

    # Extract n-grams
    ngram_scores: dict[str, float] = {}

    for sentence in sentences:
        words = re.findall(r'\b[a-z]+(?:-[a-z]+)?\b', sentence.lower())
        words = [w for w in words if w not in STOPWORDS and len(w) > 1]

        for n in range(min_length, min(max_length + 1, len(words) + 1)):
            for i in range(len(words) - n + 1):
                phrase = " ".join(words[i : i + n])
                if any(h in phrase for h in SECTION_HEADERS):
                    continue

                # Score based on position and frequency
                score = ngram_scores.get(phrase, 0) + 1.0

                # Boost phrases appearing early
                if sentences.index(sentence) < len(sentences) * 0.2:
                    score += 1.5

                ngram_scores[phrase] = score

    # Add technical terms
    for match in TECHNICAL_PATTERN.finditer(text):
        term = match.group().lower()
        if term not in STOPWORDS:
            ngram_scores[term] = ngram_scores.get(term, 0) + 3.0

    for match in ACRONYM_PATTERN.finditer(text):
        term = match.group().lower()
        if len(term) >= 2 and term not in STOPWORDS:
            ngram_scores[term] = ngram_scores.get(term, 0) + 2.0

    # Sort by score
    sorted_phrases = sorted(
        ngram_scores.items(), key=lambda x: x[1], reverse=True
    )

    results = [
        {"text": phrase, "score": round(score, 2)}
        for phrase, score in sorted_phrases[:max_phrases]
    ]

    logger.info(f"Extracted {len(results)} keyphrases from {len(text)} chars")
    return results