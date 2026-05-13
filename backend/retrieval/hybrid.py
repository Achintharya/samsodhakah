"""
Hybrid retrieval — orchestrates BM25 + vector search + reranking.
"""

from __future__ import annotations

import logging
from typing import Optional

from backend.config.settings import settings
from backend.retrieval.bm25 import bm25 as bm25_retriever

logger = logging.getLogger(__name__)

# sentence-transformers loaded lazily in _get_embedder() to avoid
# numpy/tensorflow version conflicts at import time.
HAS_SENTENCE_TRANSFORMERS = False


class HybridRetriever:
    """
    Hybrid retrieval pipeline:

    1. BM25 lexical retrieval (sparse)
    2. Vector embedding retrieval (dense, if available)
    3. Reranking with score normalization
    4. Evidence consolidation
    """

    def __init__(self) -> None:
        self._embedder = None
        self._documents: list[dict] = []  # indexed documents with embeddings
        self._is_indexed = False

    def _get_embedder(self):
        """Lazy-load sentence transformer."""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer(settings.embedding_model)
                logger.info(f"Loaded embedding model: {settings.embedding_model}")
            except Exception as e:
                logger.debug(f"Vector embeddings unavailable: {e}")
        return self._embedder

    def index_documents(self, documents: list[dict]) -> None:
        """
        Index documents for retrieval.

        Each document should have: id, text, text_for_embedding (optional), metadata.
        """
        # Index in BM25
        bm25_docs = []
        for doc in documents:
            text = doc.get("text", "")
            bm25_docs.append({
                "id": doc["id"],
                "text": text,
                "metadata": doc.get("metadata", {}),
            })
        bm25_retriever.add_documents(bm25_docs)

        # Store for vector retrieval
        self._documents = documents
        self._is_indexed = True

        # Pre-compute embeddings if possible
        embedder = self._get_embedder()
        if embedder:
            for doc in self._documents:
                text = doc.get("text_for_embedding") or doc.get("text", "")
                if text:
                    try:
                        emb = embedder.encode(text, normalize_embeddings=True)
                        doc["_embedding"] = emb.tolist()
                    except Exception as e:
                        logger.warning(f"Embedding failed for {doc['id']}: {e}")
                        doc["_embedding"] = None
                else:
                    doc["_embedding"] = None

        logger.info(
            f"Hybrid index: {len(documents)} documents "
            f"({'with' if embedder else 'without'} embeddings)"
        )

    async def search(
        self,
        query: str,
        top_k: int = 10,
        bm25_weight: float = 0.4,
        vector_weight: float = 0.6,
    ) -> list[dict]:
        """
        Hybrid search with score normalization.

        Args:
            query: Search query.
            top_k: Number of results.
            bm25_weight: Weight for lexical score (0-1).
            vector_weight: Weight for semantic score (0-1).

        Returns:
            List of results with id, score, text, metadata.
        """
        if not self._is_indexed:
            logger.warning("No documents indexed for retrieval")
            return []

        # Step 1: BM25 retrieval
        bm25_results = bm25_retriever.search(query, top_k=top_k * 2)

        # Step 2: Vector retrieval (if available)
        vector_results = []
        embedder = self._get_embedder()
        if embedder and self._documents:
            try:
                query_emb = embedder.encode(query, normalize_embeddings=True)
                scores = []
                for doc in self._documents:
                    doc_emb = doc.get("_embedding")
                    if doc_emb:
                        import math
                        # Cosine similarity
                        dot = sum(q * d for q, d in zip(query_emb, doc_emb))
                        scores.append(dot)
                    else:
                        scores.append(0.0)

                # Get top-k
                doc_scores = list(enumerate(scores))
                doc_scores.sort(key=lambda x: x[1], reverse=True)

                for doc_idx, score in doc_scores[:top_k]:
                    if score > 0:
                        doc = self._documents[doc_idx]
                        vector_results.append({
                            "id": doc["id"],
                            "score": round(float(score), 4),
                            "text": doc.get("text", "")[:500],
                            "metadata": doc.get("metadata", {}),
                        })
            except Exception as e:
                logger.warning(f"Vector search failed: {e}")

        # Step 3: Score normalization and fusion
        def _normalize(results: list[dict]) -> list[dict]:
            if not results:
                return results
            scores = [r["score"] for r in results]
            max_score = max(scores) if scores else 1.0
            min_score = min(scores) if scores else 0.0
            range_score = max_score - min_score or 1.0
            for r in results:
                r["score"] = (r["score"] - min_score) / range_score
            return results

        bm25_results = _normalize(bm25_results)
        vector_results = _normalize(vector_results)

        # Step 4: Score fusion
        fused: dict[str, dict] = {}
        for r in bm25_results:
            fused[r["id"]] = {
                "id": r["id"],
                "score": r["score"] * bm25_weight,
                "text": r["text"],
                "metadata": r.get("metadata", {}),
                "bm25_score": r["score"],
                "vector_score": 0.0,
            }

        for r in vector_results:
            if r["id"] in fused:
                fused[r["id"]]["score"] += r["score"] * vector_weight
                fused[r["id"]]["vector_score"] = r["score"]
            else:
                fused[r["id"]] = {
                    "id": r["id"],
                    "score": r["score"] * vector_weight,
                    "text": r["text"],
                    "metadata": r.get("metadata", {}),
                    "bm25_score": 0.0,
                    "vector_score": r["score"],
                }

        # Step 5: Sort and return
        results = sorted(fused.values(), key=lambda x: x["score"], reverse=True)

        logger.info(
            f"Hybrid search '{query[:50]}': {len(results)} results "
            f"(BM25: {len(bm25_results)}, Vector: {len(vector_results)})"
        )
        return results[:top_k]


# Global instance
hybrid_retriever = HybridRetriever()