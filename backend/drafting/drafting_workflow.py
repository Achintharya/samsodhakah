"""
Research Drafting Workflow - Core functionality for generating grounded research paper sections.
"""

from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.config.settings import settings
from backend.drafting.context_builder import context_builder
from backend.drafting.mistral_client import MistralClient
from backend.drafting.prompt_builders import (
    build_related_work_prompt,
    build_methodology_prompt,
    build_results_prompt,
    build_discussion_prompt,
    build_abstract_prompt
)
from backend.retrieval.scholarly import scholarly_retriever, RetrievalMode
from backend.semantic.memory import semantic_memory
from backend.verification.engine import verification_engine
from backend.evaluation.failure_corpus import failure_corpus
from backend.utils.token_metrics import token_metrics

logger = logging.getLogger(__name__)

class DraftingWorkflow:
    """
    Core drafting workflow for research paper sections.

    Provides grounding, evidence tracking, and citation support for all generated content.
    """

    def __init__(self) -> None:
        self.max_sections = settings.max_sections
        self.max_draft_tokens = settings.max_draft_tokens
        self.mistral_client = MistralClient()

    async def generate_section_outline(
        self,
        document_id: str,
        section_type: str,
        topic: str,
        related_work_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a structured outline for a research paper section.
        """
        # Determine appropriate retrieval mode based on section type
        mode_map = {
            "related_work": RetrievalMode.RELATED_WORK,
            "methodology": RetrievalMode.METHODOLOGY,
            "theory": RetrievalMode.THEORY,
            "results": RetrievalMode.RESULTS,
            "experimental_setup": RetrievalMode.EXPERIMENTAL_SETUP,
            "discussion": RetrievalMode.DISCUSSION,
            "abstract": RetrievalMode.THEORY,
        }

        retrieval_mode = mode_map.get(section_type, RetrievalMode.RELATED_WORK)

        # Simulated outline generation
        outline = {
            "section_type": section_type,
            "topic": topic,
            "generated_at": datetime.now().isoformat(),
            "key_points": [
                f"Introduction to {topic}",
                f"Key aspects of {topic} in current research",
                f"Methodologies applied to {topic}",
                f"Significant findings related to {topic}",
                f"Implications and future directions for {topic}"
            ] if section_type != "related_work" else [
                "Previous research in this area",
                "Key contributions of prior work",
                "Gaps in current understanding",
                "Research questions this work addresses",
                "Summary of main findings"
            ],
            "evidence_count": 0,
            "retrieval_mode": retrieval_mode.value,
        }

        logger.info(f"Generated outline for {section_type} section on '{topic}'")
        return outline

    async def generate_grounded_section(
        self,
        document_id: str,
        section_type: str,
        topic: str,
        related_work_id: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate a grounded research section with evidence and citation support.
        """
        warnings: List[str] = []
        token_limit = max_tokens or self.max_draft_tokens
        retrieval_mode = self._get_retrieval_mode(section_type)

        retrieval_results = await scholarly_retriever.search(
            query=topic,
            mode=retrieval_mode,
            top_k=8,
            document_id=document_id,
        )
        if not retrieval_results and related_work_id:
            retrieval_results = await scholarly_retriever.search(
                query=topic,
                mode=retrieval_mode,
                top_k=8,
                document_id=related_work_id,
            )
        if not retrieval_results:
            warnings.append("No retrieval results found; using available document-local memory only.")
            failure_corpus.record(
                "poor_retrieval",
                "Grounded drafting had no retrieval results and fell back to document-local memory.",
                {"document_id": document_id, "section_type": section_type, "topic": topic},
                severity="high",
                source="drafting",
            )

        evidence_units = self._collect_evidence_units(document_id, retrieval_results)
        semantic_units = self._collect_semantic_units(document_id, retrieval_results)
        citations = self._build_citations(evidence_units)
        if evidence_units and not citations:
            failure_corpus.record(
                "citation_mismatch",
                "Evidence was available but no citations could be constructed.",
                {
                    "document_id": document_id,
                    "section_type": section_type,
                    "topic": topic,
                    "evidence_ids": [ev.get("id") for ev in evidence_units[:10]],
                },
                severity="medium",
                source="drafting",
            )

        context_result = context_builder.build_context(
            topic=topic,
            evidence_units=evidence_units,
            semantic_units=semantic_units,
            verification_results=None,
        )
        context_stats = {
            "token_count": context_result.get("token_count", 0),
            "compression_stats": context_result.get("compression_stats", {}),
            "evidence_count": len(evidence_units),
            "semantic_unit_count": len(semantic_units),
            "retrieval_result_count": len(retrieval_results),
        }

        prompt = self._build_prompt(
            section_type=section_type,
            topic=topic,
            evidence_units=evidence_units,
            citations=citations,
            context=context_result.get("context", ""),
            max_tokens=token_limit,
        )
        structured_context = {
            "topic": topic,
            "section_type": section_type,
            "evidence_units": evidence_units,
            "semantic_units": semantic_units,
            "citations": citations,
            "retrieval_mode": retrieval_mode.value,
            "context": context_result.get("context", ""),
        }

        structured_output = None
        generation_model = "deterministic-fallback"
        if self.mistral_client.api_key:
            structured_output = await self.mistral_client.generate_grounded_section(
                prompt=prompt,
                structured_context=structured_context,
            )
            if structured_output:
                generation_model = structured_output.get("metadata", {}).get("model", settings.mistral_model)
            else:
                warnings.append("Mistral generation failed; deterministic fallback was used.")
        else:
            warnings.append("Mistral API key is not configured; deterministic fallback was used.")

        if not structured_output:
            structured_output = self._build_deterministic_structured_output(
                section_type=section_type,
                topic=topic,
                evidence_units=evidence_units,
                citations=citations,
                retrieval_mode=retrieval_mode.value,
            )

        generated_content = self._render_structured_to_prose(structured_output)
        verification_results = await self._verify_generated_claims(generated_content, evidence_units, semantic_units)
        provenance = self._build_provenance(retrieval_results, evidence_units, semantic_units, retrieval_mode.value)
        self._record_generation_quality_signals(
            document_id=document_id,
            section_type=section_type,
            topic=topic,
            evidence_units=evidence_units,
            citations=citations,
            verification_results=verification_results,
            provenance=provenance,
            context_stats=context_stats,
        )

        token_metrics.log(
            operation="grounded_section_generation",
            subsystem="drafting",
            input_tokens=len(prompt) // 4,
            output_tokens=len(generated_content) // 4,
            context_size_chars=len(context_result.get("context", "")),
            metadata={
                "section_type": section_type,
                "retrieval_mode": retrieval_mode.value,
                "model": generation_model,
                "fallback": generation_model == "deterministic-fallback",
            },
        )

        return {
            "section_type": section_type,
            "topic": topic,
            "content": generated_content,
            "generated_at": datetime.now().isoformat(),
            "context_used": {
                "topic": topic,
                "evidence_units": [ev.get("id") for ev in evidence_units],
                "citations": [cit.get("id") for cit in citations],
                "retrieval_mode": retrieval_mode.value,
                "context_preview": context_result.get("context", "")[:1000],
            },
            "evidence_units": evidence_units,
            "semantic_units": semantic_units,
            "verification_results": verification_results,
            "token_count": len(generated_content) // 4,
            "citations": citations,
            "confidence_scores": self._calculate_confidence_scores(evidence_units),
            "retrieval_results": retrieval_results,
            "provenance": provenance,
            "context_stats": context_stats,
            "structured_output": structured_output,
            "generation_model": generation_model,
            "warnings": warnings,
        }

    def _get_retrieval_mode(self, section_type: str) -> RetrievalMode:
        mode_map = {
            "related_work": RetrievalMode.RELATED_WORK,
            "methodology": RetrievalMode.METHODOLOGY,
            "theory": RetrievalMode.THEORY,
            "results": RetrievalMode.RESULTS,
            "experimental_setup": RetrievalMode.EXPERIMENTAL_SETUP,
            "discussion": RetrievalMode.DISCUSSION,
            "abstract": RetrievalMode.THEORY,
            "conclusion": RetrievalMode.DISCUSSION,
        }
        return mode_map.get(section_type, RetrievalMode.RELATED_WORK)

    def _collect_evidence_units(self, document_id: str, retrieval_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        evidence_by_id: Dict[str, Dict[str, Any]] = {}
        for ev in semantic_memory.get_evidence_for_document(document_id):
            evidence_by_id[ev.get("id", f"ev_{len(evidence_by_id)}")] = ev

        for result in retrieval_results:
            result_id = result.get("id", "")
            metadata = result.get("metadata", {}) or {}
            source_doc_id = metadata.get("document_id") or document_id
            existing = semantic_memory.evidence_units.get(result_id)
            if existing:
                evidence_by_id[existing.get("id", result_id)] = existing
                continue
            evidence_by_id[f"retrieval_{result_id}"] = {
                "id": f"retrieval_{result_id}",
                "content": result.get("text", ""),
                "role": "supports",
                "confidence": round(float(result.get("score", 0.0)), 4),
                "source_document_id": source_doc_id,
                "source_section_id": result_id if metadata.get("type") == "section" else metadata.get("section_id", ""),
                "source_semantic_unit_id": result_id if metadata.get("type") not in ["document", "section"] else "",
                "retrieval_score": result.get("score", 0.0),
                "retrieval_rank": len(evidence_by_id) + 1,
                "retrieval_metadata": metadata,
            }

        return self._select_evidence_for_drafting(list(evidence_by_id.values()))

    def _select_evidence_for_drafting(self, evidence_units: List[Dict[str, Any]], limit: int = 12) -> List[Dict[str, Any]]:
        """Select strong, diverse evidence without letting duplicate sources dominate."""
        sorted_units = sorted(evidence_units, key=lambda ev: ev.get("confidence", 0.0), reverse=True)
        selected: List[Dict[str, Any]] = []
        source_counts: Dict[str, int] = {}
        seen_content = set()

        for ev in sorted_units:
            content = (ev.get("content", "") or "").strip()
            if len(content) < 40:
                continue
            fingerprint = content.lower()[:180]
            if fingerprint in seen_content:
                continue
            source_id = ev.get("source_document_id") or "unknown"
            if source_counts.get(source_id, 0) >= 4 and len(selected) < limit:
                continue
            selected.append(ev)
            seen_content.add(fingerprint)
            source_counts[source_id] = source_counts.get(source_id, 0) + 1
            if len(selected) >= limit:
                break

        if len(selected) < min(limit, len(sorted_units)):
            for ev in sorted_units:
                if ev not in selected and len((ev.get("content", "") or "").strip()) >= 40:
                    selected.append(ev)
                if len(selected) >= limit:
                    break

        return selected[:limit]

    def _collect_semantic_units(self, document_id: str, retrieval_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unit_by_id = {u.get("id", ""): u for u in semantic_memory.get_document_semantic_units(document_id)}
        for result in retrieval_results:
            result_id = result.get("id", "")
            if result_id in semantic_memory.semantic_units:
                unit_by_id[result_id] = semantic_memory.semantic_units[result_id]
        return list(unit_by_id.values())[:12]

    def _build_prompt(
        self,
        section_type: str,
        topic: str,
        evidence_units: List[Dict],
        citations: List[Dict],
        context: str,
        max_tokens: int,
    ) -> str:
        builder_map = {
            "related_work": build_related_work_prompt,
            "methodology": build_methodology_prompt,
            "results": build_results_prompt,
            "discussion": build_discussion_prompt,
            "abstract": build_abstract_prompt,
        }
        builder = builder_map.get(section_type, build_related_work_prompt)
        base_prompt = builder(topic, evidence_units, citations, max_tokens=max_tokens)
        return "\n\n".join([
            base_prompt,
            "Grounded context selected by PromptContextBuilder:",
            context or "No compressed context was available.",
            "Return concise scholarly prose. Only make claims supported by the supplied evidence. "
            "Use citation markers like [1], [2] where relevant.",
        ])

    def _build_deterministic_structured_output(
        self,
        section_type: str,
        topic: str,
        evidence_units: List[Dict],
        citations: List[Dict],
        retrieval_mode: str,
    ) -> Dict[str, Any]:
        title = section_type.replace("_", " ").title()
        if not evidence_units:
            paragraph_texts = [
                f"{title} for {topic}. No sufficiently grounded evidence was available, so this draft is limited to a framing statement and should be expanded after ingestion or retrieval is improved."
            ]
        else:
            paragraph_texts = [
                f"Research on {topic} is grounded in {len(evidence_units)} retrieved evidence units spanning {len({ev.get('source_document_id') for ev in evidence_units if ev.get('source_document_id')})} source document(s).",
                " ".join(
                    f"Evidence {idx + 1} indicates {ev.get('content', '').strip()[:220]}{'...' if len(ev.get('content', '')) > 220 else ''} [{idx + 1}]"
                    for idx, ev in enumerate(evidence_units[:3])
                    if ev.get("content")
                ),
                "Together, these sources support a cautious synthesis while preserving explicit provenance for verification and export.",
            ]

        paragraphs = []
        for idx, text in enumerate([p for p in paragraph_texts if p.strip()]):
            para_evidence = evidence_units[idx:idx + 3] or evidence_units[:3]
            paragraphs.append({
                "text": text,
                "citations": citations[:min(3, len(citations))],
                "evidence_ids": [ev.get("id") for ev in para_evidence],
                "confidence": self._calculate_confidence_scores(para_evidence).get("overall", 0.0),
                "provenance": {
                    "source_documents": sorted({ev.get("source_document_id") for ev in para_evidence if ev.get("source_document_id")}),
                    "retrieval_mode": retrieval_mode,
                },
            })
        return {
            "section_title": title,
            "paragraphs": paragraphs,
            "metadata": {
                "token_usage": {"total_tokens": sum(len(p["text"]) for p in paragraphs) // 4},
                "model": "deterministic-fallback",
                "confidence": self._calculate_confidence_scores(evidence_units).get("overall", 0.0),
            },
        }

    async def _verify_generated_claims(
        self,
        content: str,
        evidence_units: List[Dict],
        semantic_units: List[Dict],
    ) -> List[Dict[str, Any]]:
        source_texts: Dict[str, str] = {}
        for ev in evidence_units[:8]:
            if ev.get("content"):
                source_texts[ev.get("id", f"evidence_{len(source_texts)}")] = ev.get("content", "")
        for unit in semantic_units[:8]:
            if unit.get("content"):
                source_texts[unit.get("id", f"semantic_{len(source_texts)}")] = unit.get("content", "")

        results = []
        for claim in self._extract_claims_from_content(content)[:5]:
            results.append(await verification_engine.verify_claim(claim, source_texts))
        return results

    def _build_provenance(
        self,
        retrieval_results: List[Dict[str, Any]],
        evidence_units: List[Dict[str, Any]],
        semantic_units: List[Dict[str, Any]],
        retrieval_mode: str,
    ) -> Dict[str, Any]:
        return {
            "retrieval_mode": retrieval_mode,
            "source_documents": sorted({ev.get("source_document_id") for ev in evidence_units if ev.get("source_document_id")}),
            "evidence_chain": [
                {
                    "evidence_unit_id": ev.get("id"),
                    "document_id": ev.get("source_document_id"),
                    "section_id": ev.get("source_section_id"),
                    "semantic_unit_id": ev.get("source_semantic_unit_id"),
                    "retrieval_score": ev.get("retrieval_score", ev.get("confidence", 0.0)),
                }
                for ev in evidence_units
            ],
            "semantic_unit_ids": [u.get("id") for u in semantic_units if u.get("id")],
            "retrieval_result_ids": [r.get("id") for r in retrieval_results],
        }

    def _record_generation_quality_signals(
        self,
        document_id: str,
        section_type: str,
        topic: str,
        evidence_units: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        verification_results: List[Dict[str, Any]],
        provenance: Dict[str, Any],
        context_stats: Dict[str, Any],
    ) -> None:
        """Log practical quality failures for later workflow tuning."""
        base_payload = {
            "document_id": document_id,
            "section_type": section_type,
            "topic": topic,
            "evidence_count": len(evidence_units),
            "citation_count": len(citations),
            "context_stats": context_stats,
        }

        unsupported = [
            result for result in verification_results
            if result.get("evidence_count", 0) == 0 or result.get("confidence", 0.0) < 0.35
        ]
        contradicted = [
            result for result in verification_results
            if result.get("contradicted_count", 0) > 0 or result.get("verdict") == "contradicted"
        ]
        if unsupported:
            failure_corpus.record(
                "unsupported_claim",
                "Generated section contains low-confidence or unsupported claims.",
                {**base_payload, "claims": [r.get("claim") for r in unsupported[:5]]},
                severity="medium",
                source="drafting_verification",
            )
        if contradicted:
            failure_corpus.record(
                "contradictory_output",
                "Generated section contains claims contradicted by retrieved sources.",
                {**base_payload, "claims": [r.get("claim") for r in contradicted[:5]]},
                severity="high",
                source="drafting_verification",
            )
        if len(provenance.get("evidence_chain", [])) < max(1, min(3, len(evidence_units))):
            failure_corpus.record(
                "weak_provenance",
                "Generated section has sparse provenance relative to available evidence.",
                {**base_payload, "provenance": provenance},
                severity="medium",
                source="drafting",
            )

    def _render_structured_to_prose(self, structured_result: Dict[str, Any]) -> str:
        """
        Convert structured Mistral output to prose format for compatibility.
        """
        prose_parts = [structured_result["section_title"]]
        for paragraph in structured_result["paragraphs"]:
            prose_parts.append(paragraph["text"])
        return "\n\n".join(prose_parts)

    def _extract_claims_from_content(self, content: str) -> List[str]:
        """
        Extract claims from generated content for verification.
        """
        sentences = content.split('. ')
        claims = [s for s in sentences if s.strip() and len(s.strip()) > 20]
        return claims[:10]

    def _build_citations(self, evidence_units: List[Dict]) -> List[Dict]:
        """
        Build citation information for evidence units.
        """
        citations = []
        seen_sources = set()
        for ev in evidence_units[:10]:
            source_doc_id = ev.get("source_document_id")
            if source_doc_id and source_doc_id not in seen_sources:
                doc = semantic_memory.get_document(source_doc_id) or {}
                title = doc.get("title") or doc.get("filename") or source_doc_id
                year = doc.get("year") or doc.get("publication_year") or "n.d."
                authors = doc.get("authors") or doc.get("author") or []
                if isinstance(authors, str):
                    authors = [authors]
                citation = {
                    "id": f"cite_{len(citations) + 1}",
                    "key": f"{source_doc_id}_{len(citations) + 1}",
                    "entry_type": doc.get("entry_type", "article"),
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "source_document": title,
                    "source_document_id": source_doc_id,
                    "content_preview": ev.get("content", "")[:100] + ("..." if len(ev.get("content", "")) > 100 else ""),
                    "role": ev.get("role", "supports"),
                    "confidence": ev.get("confidence", 0.0),
                }
                citations.append(citation)
                seen_sources.add(source_doc_id)
        return citations

    def _calculate_confidence_scores(self, evidence_units: List[Dict]) -> Dict[str, float]:
        """
        Calculate overall confidence scores for the evidence used.
        """
        if not evidence_units:
            return {"overall": 0.0, "supported": 0.0, "contradicted": 0.0}

        confidences = [ev.get("confidence", 0.0) for ev in evidence_units]
        return {
            "overall": sum(confidences) / len(confidences) if confidences else 0.0,
            "supported": sum(c for c in confidences if c > 0.5) / len([c for c in confidences if c > 0.5]) if any(c > 0.5 for c in confidences) else 0.0,
            "contradicted": sum(c for c in confidences if c < 0.3) / len([c for c in confidences if c < 0.3]) if any(c < 0.3 for c in confidences) else 0.0,
        }

# Global instance
drafting_workflow = DraftingWorkflow()