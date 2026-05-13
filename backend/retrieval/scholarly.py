"""
Scholarly retrieval — specialized retrieval modes for research paper writing.
"""

from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any, Set
from enum import Enum

from backend.config.settings import settings
from backend.retrieval.hybrid import hybrid_retriever
from backend.semantic.memory import semantic_memory
from backend.evaluation.failure_corpus import failure_corpus

logger = logging.getLogger(__name__)


class RetrievalMode(str, Enum):
    """Enumeration of scholarly retrieval modes."""
    RELATED_WORK = "related_work"
    METHODOLOGY = "methodology"
    THEORY = "theory"
    CONTRADICTION_SCAN = "contradiction_scan"
    RESULTS = "results"
    EXPERIMENTAL_SETUP = "experimental_setup"
    DISCUSSION = "discussion"


class ScholarlyRetriever:
    """
    Scholarly retrieval system with specialized modes for research paper writing.
    
    Optimized for actual research paper writing scenarios rather than generic semantic search.
    """

    def __init__(self) -> None:
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the scholarly retriever with indexed documents."""
        # Build index if not already built
        if not hybrid_retriever._is_indexed:
            # Get all texts from semantic memory for indexing
            texts = semantic_memory.get_all_texts_for_indexing()
            if texts:
                hybrid_retriever.index_documents(texts)
                logger.info(f"Indexed {len(texts)} texts for scholarly retrieval")
        
        self._initialized = True

    async def search(
        self,
        query: str,
        mode: RetrievalMode = RetrievalMode.RELATED_WORK,
        top_k: int = 10,
        document_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform scholarly search with specialized retrieval modes.
        
        Args:
            query: Search query string
            mode: Retrieval mode (related_work, methodology, etc.)
            top_k: Number of results to return
            document_id: Optional filter for specific document
            
        Returns:
            List of retrieval results with id, score, text, metadata
        """
        if not self._initialized:
            self.initialize()
            
        # Apply mode-specific filters to the query
        filtered_query = self._apply_mode_filter(query, mode)
        
        # Add document-specific filtering if requested
        if document_id:
            filtered_query = f"{filtered_query} document_id:{document_id}"
            
        # Perform hybrid search
        results = await hybrid_retriever.search(
            query=filtered_query,
            top_k=top_k * 2,  # Get more results for better filtering
            bm25_weight=0.3,
            vector_weight=0.7,
        )
        
        # Apply mode-specific post-processing
        processed_results = self._post_process_results(results, mode, top_k)
        self._record_retrieval_quality_signals(query, mode, processed_results, document_id)
        
        logger.info(
            f"Scholarly search '{query[:50]}...' in mode '{mode.value}': "
            f"{len(processed_results)} results"
        )
        return processed_results

    def _apply_mode_filter(self, query: str, mode: RetrievalMode) -> str:
        """
        Apply domain-specific filters to query based on retrieval mode.
        
        Args:
            query: Original search query
            mode: Retrieval mode
            
        Returns:
            Filtered query string
        """
        mode_filters = {
            RetrievalMode.RELATED_WORK: [
                "literature review", "related work", "background", "survey", 
                "previous studies", "existing approaches", "prior art", 
                "comparative study", "related research", "state of the art",
                "related publications", "previous work"
            ],
            RetrievalMode.METHODOLOGY: [
                "methodology", "approach", "technique", "procedure", 
                "experimental design", "implementation", "framework", 
                "method", "process", "strategy", "workflow",
                "research method", "study design", "analysis method"
            ],
            RetrievalMode.THEORY: [
                "theory", "concept", "principle", "model", "hypothesis", 
                "axiom", "foundation", "underlying mechanism", "mathematical", 
                "formulation", "theorem", "proof", "assumption",
                "theoretical framework", "conceptual model", "mathematical model"
            ],
            RetrievalMode.CONTRADICTION_SCAN: [
                "contradict", "conflict", "inconsistency", "discrepancy", 
                "opposition", "challenge", "disprove", "reject", "debunk", 
                "counterexample", "exception", "limitation",
                "limitation", "shortcoming", "criticism", "flaw"
            ],
            RetrievalMode.RESULTS: [
                "result", "finding", "outcome", "data", "observation", 
                "measurement", "experiment", "study", "analysis", 
                "statistical", "quantitative", "qualitative", "performance",
                "evaluation", "comparison", "benchmark", "dataset"
            ],
            RetrievalMode.EXPERIMENTAL_SETUP: [
                "experiment", "testing", "trial", "setup", "configuration", 
                "equipment", "materials", "tools", "hardware", "software", 
                "procedure", "protocol", "method", "approach",
                "experimental design", "testbed", "platform", "environment"
            ],
            RetrievalMode.DISCUSSION: [
                "discussion", "interpretation", "analysis", "implication", 
                "conclusion", "summary", "overview", "synthesis", 
                "evaluation", "assessment", "critique", "commentary",
                "significance", "impact", "meaning", "value", "benefit"
            ]
        }
        
        # Add mode-specific keywords to query for better matching
        if mode in mode_filters:
            mode_keywords = mode_filters[mode]
            # Add weighted keywords to query
            weighted_query = query
            for keyword in mode_keywords[:3]:  # Take first 3 keywords
                weighted_query = f"{keyword} {weighted_query}"
                
            return weighted_query
            
        return query

    def _post_process_results(
        self, 
        results: List[Dict[str, Any]], 
        mode: RetrievalMode, 
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Apply mode-specific post-processing to refine results.
        
        Args:
            results: Raw retrieval results
            mode: Retrieval mode
            top_k: Target number of results
            
        Returns:
            Processed and filtered results
        """
        if not results:
            return []
            
        # Filter results based on relevance to the mode
        filtered_results = []
        mode_terms = self._mode_terms(mode)
        
        for result in results:
            # Basic filtering by metadata if available
            metadata = result.get("metadata", {})
            result_type = metadata.get("type", "")
            text = result.get("text", "") or ""
            lowered_text = text.lower()
            
            # Mode-specific relevance scoring
            relevance_score = 1.0
            
            # Penalize irrelevant types for specific modes
            if mode in [RetrievalMode.RELATED_WORK, RetrievalMode.METHODOLOGY, RetrievalMode.THEORY]:
                # These modes prefer semantic units, sections, and documents with research-related content
                if result_type in ["document"]:
                    # Documents are generally relevant
                    relevance_score *= 1.0
                elif result_type in ["section"]:
                    # Section titles matter for these modes
                    relevance_score *= 0.9
                elif result_type in ["semantic_unit"]:
                    # Semantic units are most relevant
                    relevance_score *= 1.1
                else:
                    # Other types are less relevant
                    relevance_score *= 0.7
                    
            elif mode == RetrievalMode.CONTRADICTION_SCAN:
                # Look for evidence and claims that might contradict
                if result_type in ["semantic_unit", "evidence_unit"]:
                    relevance_score *= 1.2
                elif result_type in ["section"]:
                    relevance_score *= 0.8
                else:
                    relevance_score *= 0.6
            elif mode in [RetrievalMode.RESULTS, RetrievalMode.EXPERIMENTAL_SETUP, RetrievalMode.DISCUSSION]:
                if result_type in ["evidence_unit", "experimental_result", "metric", "methodology", "section"]:
                    relevance_score *= 1.15
                elif result_type == "document":
                    relevance_score *= 0.75

            matched_terms = sum(1 for term in mode_terms if term in lowered_text)
            if matched_terms:
                relevance_score *= min(1.35, 1.0 + matched_terms * 0.07)

            if metadata.get("role") == "contradicts" or any(
                term in lowered_text for term in ["contradict", "conflict", "limitation", "however", "in contrast"]
            ):
                result["contradiction_signal"] = True
                if mode in [RetrievalMode.CONTRADICTION_SCAN, RetrievalMode.DISCUSSION]:
                    relevance_score *= 1.2

            if metadata.get("type") == "evidence_unit":
                relevance_score *= 1.1
                    
            # Apply relevance score and filter by threshold
            result["relevance_score"] = relevance_score
            if relevance_score >= 0.5:  # Minimum relevance threshold
                filtered_results.append(result)
        
        # Sort by combined score, then preserve source diversity for drafting usefulness.
        filtered_results.sort(key=lambda x: x.get("score", 0) * x.get("relevance_score", 1), reverse=True)

        return self._select_diverse_results(filtered_results, top_k)

    def _mode_terms(self, mode: RetrievalMode) -> List[str]:
        """Compact term list used for post-retrieval reranking."""
        terms = {
            RetrievalMode.RELATED_WORK: ["related", "prior", "previous", "survey", "literature", "baseline"],
            RetrievalMode.METHODOLOGY: ["method", "approach", "procedure", "workflow", "implementation", "protocol"],
            RetrievalMode.THEORY: ["theory", "model", "principle", "assumption", "framework", "formulation"],
            RetrievalMode.CONTRADICTION_SCAN: ["contradict", "conflict", "limitation", "discrepancy", "however", "challenge"],
            RetrievalMode.RESULTS: ["result", "finding", "metric", "performance", "evaluation", "benchmark"],
            RetrievalMode.EXPERIMENTAL_SETUP: ["setup", "dataset", "configuration", "tool", "environment", "protocol"],
            RetrievalMode.DISCUSSION: ["discussion", "implication", "limitation", "interpretation", "future", "significance"],
        }
        return terms.get(mode, [])

    def _select_diverse_results(self, results: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """Prefer relevant results while avoiding one-source evidence collapse."""
        selected: List[Dict[str, Any]] = []
        source_counts: Dict[str, int] = {}
        seen_texts: Set[str] = set()

        for result in results:
            metadata = result.get("metadata", {}) or {}
            source_id = metadata.get("document_id") or result.get("id", "unknown")
            fingerprint = (result.get("text", "") or "").strip().lower()[:180]
            if fingerprint and fingerprint in seen_texts:
                continue
            if source_counts.get(source_id, 0) >= 3 and len(selected) < top_k:
                continue

            result["diversity_rank"] = source_counts.get(source_id, 0) + 1
            selected.append(result)
            source_counts[source_id] = source_counts.get(source_id, 0) + 1
            if fingerprint:
                seen_texts.add(fingerprint)
            if len(selected) >= top_k:
                break

        if len(selected) < top_k:
            for result in results:
                if result not in selected:
                    selected.append(result)
                if len(selected) >= top_k:
                    break

        return selected[:top_k]

    def _record_retrieval_quality_signals(
        self,
        query: str,
        mode: RetrievalMode,
        results: List[Dict[str, Any]],
        document_id: Optional[str],
    ) -> None:
        """Log lightweight failure-corpus entries for poor retrieval signals."""
        if not results:
            failure_corpus.record(
                "poor_retrieval",
                "Scholarly retrieval returned no results.",
                {"query": query, "mode": mode.value, "document_id": document_id},
                severity="high",
                source="retrieval",
            )
            return

        top_score = max(float(r.get("score", 0.0) or 0.0) for r in results)
        source_count = len({(r.get("metadata", {}) or {}).get("document_id") or r.get("id") for r in results})
        if top_score < 0.15 or (len(results) >= 4 and source_count <= 1):
            failure_corpus.record(
                "poor_retrieval",
                "Retrieval produced low-scoring or low-diversity evidence.",
                {
                    "query": query,
                    "mode": mode.value,
                    "document_id": document_id,
                    "top_score": top_score,
                    "result_count": len(results),
                    "source_count": source_count,
                    "result_ids": [r.get("id") for r in results[:8]],
                },
                severity="medium",
                source="retrieval",
            )


# Global instance
scholarly_retriever = ScholarlyRetriever()


def initialize_scholarly_retrieval() -> None:
    """Initialize the scholarly retrieval system."""
    scholarly_retriever.initialize()