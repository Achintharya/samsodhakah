"""
BM25 lexical retrieval — Okapi BM25 for sparse retrieval.
"""

from __future__ import annotations

import math
import logging
from collections import Counter
from typing import Optional

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class BM25Retriever:
    """
    Okapi BM25 retrieval for sparse text search.

    Uses in-memory index. Documents must be added before querying.
    """

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self.k1 = k1
        self.b = b
        self.documents: list[dict] = []  # each: {"id": str, "text": str, "metadata": dict}
        self._avg_doc_length: float = 0.0
        self._doc_lengths: list[int] = []
        self._inverted_index: dict[str, list[tuple[int, int]]] = {}  # term -> [(doc_idx, freq)]
        self._is_indexed = False

    def add_document(self, doc_id: str, text: str, metadata: Optional[dict] = None) -> None:
        """Add a document to the index."""
        self.documents.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata or {},
        })
        self._is_indexed = False

    def add_documents(self, docs: list[dict]) -> None:
        """Add multiple documents. Each should have 'id' and 'text' keys."""
        for doc in docs:
            self.add_document(doc["id"], doc["text"], doc.get("metadata"))
        self._is_indexed = False

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenizer — lowercase, split on non-alphanumeric."""
        import re
        return re.findall(r"\b[a-z0-9]+\b", text.lower())

    def _build_index(self) -> None:
        """Build or rebuild the inverted index."""
        self._inverted_index = {}
        self._doc_lengths = []

        for doc_idx, doc in enumerate(self.documents):
            tokens = self._tokenize(doc["text"])
            self._doc_lengths.append(len(tokens))

            # Count term frequencies for this document
            term_counts = Counter(tokens)
            for term, freq in term_counts.items():
                if term not in self._inverted_index:
                    self._inverted_index[term] = []
                self._inverted_index[term].append((doc_idx, freq))

        self._avg_doc_length = (
            sum(self._doc_lengths) / len(self._doc_lengths)
            if self._doc_lengths else 0
        )
        self._is_indexed = True
        logger.info(
            f"BM25 index built: {len(self.documents)} documents, "
            f"{len(self._inverted_index)} unique terms"
        )

    def _ensure_indexed(self) -> None:
        if not self._is_indexed:
            self._build_index()

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """
        Search the index with BM25 scoring.

        Args:
            query: Search query string.
            top_k: Number of results to return.

        Returns:
            List of dicts with 'id', 'score', 'text', 'metadata' keys, sorted by score desc.
        """
        self._ensure_indexed()
        if not self.documents:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        n_docs = len(self.documents)
        scores = [0.0] * n_docs

        for term in set(query_tokens):
            if term not in self._inverted_index:
                continue

            # IDF component
            df = len(self._inverted_index[term])
            idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)

            for doc_idx, freq in self._inverted_index[term]:
                doc_len = self._doc_lengths[doc_idx]

                # TF component with saturation
                numerator = freq * (self.k1 + 1)
                denominator = freq + self.k1 * (
                    1 - self.b + self.b * (doc_len / self._avg_doc_length)
                )
                tf_component = numerator / denominator if denominator > 0 else 0

                scores[doc_idx] += idf * tf_component

        # Build results
        doc_scores = list(enumerate(scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for doc_idx, score in doc_scores[:top_k]:
            if score > 0:
                doc = self.documents[doc_idx]
                results.append({
                    "id": doc["id"],
                    "score": round(score, 4),
                    "text": doc["text"][:500],  # text preview
                    "metadata": doc["metadata"],
                })

        logger.info(
            f"BM25 search '{query[:50]}': "
            f"{len(results)} results from {n_docs} documents"
        )
        return results


# Global instance
bm25 = BM25Retriever(
    k1=settings.bm25_k1,
    b=settings.bm25_b,
)