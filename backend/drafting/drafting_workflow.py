"""
Research Drafting Workflow - Core functionality for generating grounded research paper sections.
"""

from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.config.settings import settings
from backend.drafting.context_builder import context_builder
from backend.retrieval.scholarly import scholarly_retriever, RetrievalMode
from backend.semantic.memory import semantic_memory
from backend.verification.engine import verification_engine
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

    async def generate_section_outline(
        self,
        document_id: str,
        section_type: str,
        topic: str,
        related_work_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a structured outline for a research paper section.
        
        Args:
            document_id: ID of the source document
            section_type: Type of section (related_work, methodology, results, etc.)
            topic: Main topic to cover
            related_work_id: Optional related work document ID
            
        Returns:
            Section outline with structure and key points
        """
        # Determine appropriate retrieval mode based on section type
        mode_map = {
            "related_work": RetrievalMode.RELATED_WORK,
            "methodology": RetrievalMode.METHODOLOGY,
            "theory": RetrievalMode.THEORY,
            "results": RetrievalMode.RESULTS,
            "experimental_setup": RetrievalMode.EXPERIMENTAL_SETUP,
            "discussion": RetrievalMode.DISCUSSION,
        }
        
        retrieval_mode = mode_map.get(section_type, RetrievalMode.RELATED_WORK)
        
        # Get related evidence for context
        evidence = []
        if related_work_id:
            # Get evidence from related work
            related_evidence = semantic_memory.get_evidence_for_document(related_work_id)
            evidence.extend(related_evidence)
            
        # Get evidence based on section type
        if retrieval_mode != RetrievalMode.RELATED_WORK:
            # Retrieve relevant documents using scholarly retrieval
            related_results = await scholarly_retriever.search(
                query=topic,
                mode=retrieval_mode,
                top_k=5,
                document_id=document_id if document_id else None,
            )
            
            # Extract evidence from retrieved documents
            for result in related_results:
                # In a real implementation, we would fetch the actual documents
                # and extract evidence units, but for now we'll simulate this
                pass
                
        # Simulated outline generation (would be powered by LLM in real implementation)
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
            "evidence_count": len(evidence),
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
        
        Args:
            document_id: ID of the source document
            section_type: Type of section (related_work, methodology, etc.)
            topic: Main topic to cover
            related_work_id: Optional related work document ID
            max_tokens: Optional override for token limit
            
        Returns:
            Generated section with evidence tracking and citation links
        """
        # Determine appropriate retrieval mode based on section type
        mode_map = {
            "related_work": RetrievalMode.RELATED_WORK,
            "methodology": RetrievalMode.METHODOLOGY,
            "theory": RetrievalMode.THEORY,
            "results": RetrievalMode.RESULTS,
            "experimental_setup": RetrievalMode.EXPERIMENTAL_SETUP,
            "discussion": RetrievalMode.DISCUSSION,
        }
        
        retrieval_mode = mode_map.get(section_type, RetrievalMode.RELATED_WORK)
        
        # Get relevant evidence and semantic units
        evidence_units = []
        semantic_units = []
        verification_results = []
        
        # Get evidence from the document itself
        evidence_units.extend(semantic_memory.get_evidence_for_document(document_id))
        
        # Get related semantic units from the document
        semantic_units.extend(semantic_memory.get_document_semantic_units(document_id))
        
        # Get related work evidence if specified
        if related_work_id:
            evidence_units.extend(semantic_memory.get_evidence_for_document(related_work_id))
            semantic_units.extend(semantic_memory.get_document_semantic_units(related_work_id))
            
        # Retrieve additional relevant documents using scholarly retrieval
        if retrieval_mode != RetrievalMode.RELATED_WORK:
            # In a real implementation, this would fetch actual related documents
            # and their evidence units for inclusion in context
            pass
            
        # Build context using PromptContextBuilder
        context_result = context_builder.build_context(
            topic=topic,
            evidence_units=evidence_units,
            semantic_units=semantic_units,
            verification_results=verification_results
        )
        
        # Simulate LLM generation (would be replaced with actual LLM call)
        # This demonstrates the grounding approach
        generated_content = self._simulate_llm_generation(
            topic=topic,
            context=context_result["context"],
            section_type=section_type,
            evidence_units=evidence_units
        )
        
        # Verify claims in the generated content
        claims_to_verify = self._extract_claims_from_content(generated_content)
        verification_results = []
        
        if claims_to_verify:
            # In a real implementation, this would call the verification engine
            # For now, we'll just record that verification would happen
            pass
            
        # Build final section result
        section_result = {
            "section_type": section_type,
            "topic": topic,
            "content": generated_content,
            "generated_at": datetime.now().isoformat(),
            "context_used": context_result,
            "evidence_units": evidence_units[:10],  # Limit for brevity
            "semantic_units": semantic_units[:10],  # Limit for brevity
            "verification_results": verification_results,
            "token_count": context_result["token_count"],
            "citations": self._build_citations(evidence_units),
            "confidence_scores": self._calculate_confidence_scores(evidence_units),
        }
        
        # Track token metrics
        token_metrics.log(
            operation="draft_section",
            subsystem="workflow",
            input_tokens=context_result["compression_stats"]["original_chars"] // 4,
            context_size_chars=context_result["compression_stats"]["original_chars"],
            compressed_size_chars=context_result["compression_stats"]["compressed_chars"],
            metadata={
                "section_type": section_type,
                "topic": topic,
                "token_count": context_result["token_count"],
                "evidence_count": len(evidence_units),
            }
        )
        
        logger.info(
            f"Generated {section_type} section for '{topic}' with "
            f"{len(evidence_units)} evidence units ({context_result['token_count']} tokens)"
        )
        
        return section_result

    def _simulate_llm_generation(
        self, 
        topic: str, 
        context: str, 
        section_type: str,
        evidence_units: List[Dict]
    ) -> str:
        """
        Simulate LLM generation with grounding based on context.
        
        In a real implementation, this would be replaced with actual LLM calls.
        """
        # This simulates how a grounded section would look based on the evidence
        intro_lines = [
            f"This section addresses {topic}, drawing upon the available evidence.",
            f"Based on the reviewed literature and experimental findings, {topic} can be understood as follows:"
        ]
        
        # Add evidence-based statements
        evidence_summary = []
        for i, ev in enumerate(evidence_units[:5]):  # Limit to 5 examples
            role = ev.get("role", "supports")
            if role == "supports":
                evidence_summary.append(f"- {ev.get('content', '')[:100]}...")
            elif role == "contradicts":
                evidence_summary.append(f"- However, {ev.get('content', '')[:100]}...")
                
        # Combine intro and evidence
        content_parts = intro_lines + evidence_summary
        
        # Add closing statement based on section type
        if section_type == "related_work":
            closing = "This summary represents the current state of research in this field."
        elif section_type == "methodology":
            closing = "The methods described here are widely adopted in contemporary practice."
        elif section_type == "results":
            closing = "These findings align with previous research in the area."
        else:
            closing = "This perspective builds upon and extends current understanding."
            
        content_parts.append(closing)
        
        return "\n\n".join(content_parts)

    def _extract_claims_from_content(self, content: str) -> List[str]:
        """
        Extract claims from generated content for verification.
        
        Note: In reality, this would be more sophisticated and probably done
        during the LLM generation process itself.
        """
        # This is a simplified extraction - in practice would use NLP
        # or LLM-based claim extraction
        sentences = content.split('. ')
        claims = [s for s in sentences if s.strip() and len(s.strip()) > 20]
        return claims[:10]  # Limit to first 10 claims

    def _build_citations(self, evidence_units: List[Dict]) -> List[Dict]:
        """
        Build citation information for evidence units.
        
        Args:
            evidence_units: List of evidence unit dictionaries
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        for ev in evidence_units[:10]:  # Limit to first 10 for brevity
            source_doc_id = ev.get("source_document_id")
            if source_doc_id:
                doc = semantic_memory.get_document(source_doc_id)
                if doc:
                    citation = {
                        "id": ev.get("id", ""),
                        "source_document": doc.get("title", "Unknown"),
                        "source_document_id": source_doc_id,
                        "content_preview": ev.get("content", "")[:100] + "...",
                        "role": ev.get("role", "supports"),
                        "confidence": ev.get("confidence", 0.0),
                    }
                    citations.append(citation)
                    
        return citations

    def _calculate_confidence_scores(self, evidence_units: List[Dict]) -> Dict[str, float]:
        """
        Calculate overall confidence scores for the evidence used.
        
        Args:
            evidence_units: List of evidence unit dictionaries
            
        Returns:
            Dictionary of confidence metrics
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