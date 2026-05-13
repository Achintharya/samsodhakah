"""
Verification User Experience - Enhanced UI-friendly verification results.
"""

from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.verification.engine import verification_engine
from backend.semantic.memory import semantic_memory

logger = logging.getLogger(__name__)


class VerificationUX:
    """
    Enhanced verification system focused on user experience for research writing.
    
    Provides clear, actionable feedback about claim support and evidence quality
    for researchers drafting papers.
    """

    def __init__(self) -> None:
        pass

    async def verify_section_claims(
        self,
        document_id: str,
        section_content: str,
        section_type: str,
        related_work_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Verify claims in section content against source documents.
        
        Args:
            document_id: ID of the source document
            section_content: Content of the section to verify
            section_type: Type of section (methodology, results, etc.)
            related_work_id: Optional related work document ID
            
        Returns:
            Enhanced verification results with user-friendly feedback
        """
        # Extract claims from section content (simplified approach)
        claims = self._extract_claims_from_content(section_content)
        
        source_texts, source_catalog = self._build_source_texts(document_id, related_work_id)
        
        # Verify each claim
        verification_results = []
        for claim in claims[:10]:  # Limit to first 10 claims for performance
            if claim.strip():
                try:
                    engine_result = await verification_engine.verify_claim(claim, source_texts)
                    verification_results.append(
                        self._to_ui_verification_result(engine_result, source_catalog)
                    )
                except Exception as e:
                    logger.warning(f"Error verifying claim '{claim[:50]}...': {e}")
                    # Add placeholder result for failed verification
                    verification_results.append({
                        "claim": claim,
                        "verdict": "unverifiable",
                        "confidence": 0.0,
                        "evidence_count": 0,
                        "details": "Verification failed",
                        "supporting_evidence": [],
                        "contradictions": [],
                        "warnings": ["Verification error occurred"],
                    })
        
        # Build user-friendly summary
        summary = self._build_verification_summary(verification_results)
        
        result = {
            "section_id": f"{document_id}_{section_type}",
            "section_type": section_type,
            "claim_count": len(claims),
            "verification_results": verification_results,
            "summary": summary,
            "source_count": len(source_texts),
            "evidence_usage": self._summarize_evidence_usage(verification_results),
            "generated_at": datetime.now().isoformat(),
        }
        
        logger.info(
            f"Verified {len(claims)} claims in {section_type} section "
            f"from document {document_id}"
        )
        
        return result

    def _extract_claims_from_content(self, content: str) -> List[str]:
        """
        Extract claims from section content.
        
        In a real implementation, this would use NLP or LLM-based extraction.
        """
        # This is a simplified approach - in practice would be more sophisticated
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        # Filter for potentially factual/claim-like statements
        claims = []
        for sentence in sentences:
            # Skip very short sentences or those that look like introductions
            if len(sentence) > 30 and not any(keyword in sentence.lower() for keyword in [
                "this paper", "in this work", "we propose", "the following", "accordingly"
            ]):
                # Simplified claim detection - look for statements that assert facts
                if any(word in sentence.lower() for word in [
                    "shows", "indicates", "demonstrates", "found", "reveals", 
                    "suggests", "implies", "confirms", "establishes", "proves"
                ]):
                    claims.append(sentence + ".")
                    
        if not claims:
            claims = [s + "." for s in sentences if len(s) > 50][:10]
        return claims[:15]  # Limit to 15 claims for performance

    def _build_source_texts(
        self,
        document_id: str,
        related_work_id: Optional[str] = None,
    ) -> tuple[Dict[str, str], Dict[str, Dict[str, Any]]]:
        """Collect real section, semantic-unit, and evidence text for verification."""
        source_texts: Dict[str, str] = {}
        source_catalog: Dict[str, Dict[str, Any]] = {}
        document_ids = [document_id] + ([related_work_id] if related_work_id else [])

        for doc_id in [doc for doc in document_ids if doc]:
            doc = semantic_memory.get_document(doc_id) or {}
            title = doc.get("title") or doc.get("filename") or doc_id

            for section in semantic_memory.get_document_sections(doc_id):
                content = section.get("content", "")
                if content.strip():
                    source_id = section.get("id") or f"section_{len(source_texts)}"
                    source_texts[source_id] = content
                    source_catalog[source_id] = {
                        "type": "section",
                        "source_document_id": doc_id,
                        "source_document": title,
                        "title": section.get("title", "Section"),
                        "content": content,
                    }

            for unit in semantic_memory.get_document_semantic_units(doc_id):
                content = unit.get("content", "")
                if content.strip():
                    source_id = unit.get("id") or f"semantic_{len(source_texts)}"
                    source_texts[source_id] = content
                    source_catalog[source_id] = {
                        "type": unit.get("unit_type", "semantic_unit"),
                        "source_document_id": doc_id,
                        "source_document": title,
                        "title": unit.get("unit_type", "Semantic unit"),
                        "content": content,
                    }

            for evidence in semantic_memory.get_evidence_for_document(doc_id):
                content = evidence.get("content", "")
                if content.strip():
                    source_id = evidence.get("id") or f"evidence_{len(source_texts)}"
                    source_texts[source_id] = content
                    source_catalog[source_id] = {
                        "type": "evidence",
                        "source_document_id": doc_id,
                        "source_document": title,
                        "title": evidence.get("role", "Evidence"),
                        "content": content,
                        "confidence": evidence.get("confidence", 0.0),
                    }

        return dict(list(source_texts.items())[:30]), source_catalog

    def _to_ui_verification_result(
        self,
        engine_result: Dict[str, Any],
        source_catalog: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Adapt VerificationEngine output to the existing frontend-friendly shape."""
        source_results = engine_result.get("source_results", [])
        ranked_sources = sorted(
            source_results,
            key=lambda r: r.get("combined_confidence", 0.0),
            reverse=True,
        )
        supporting_evidence = []
        for result in ranked_sources[:5]:
            source_id = result.get("source_id", "")
            source = source_catalog.get(source_id, {})
            content = source.get("content", "")
            confidence = result.get("combined_confidence", 0.0)
            if confidence <= 0 and not content:
                continue
            supporting_evidence.append({
                "id": source_id,
                "source_document": source.get("source_document", source_id),
                "source_document_id": source.get("source_document_id", ""),
                "source_type": source.get("type", "source"),
                "content_preview": content[:240] + ("..." if len(content) > 240 else ""),
                "confidence": round(confidence, 4),
                "role": "supports" if confidence >= 0.5 else "weak_support",
                "lexical": result.get("lexical", {}),
                "numerical": result.get("numerical", {}),
            })

        warnings = []
        if engine_result.get("confidence", 0.0) < 0.5:
            warnings.append("Low evidence overlap; review or add stronger source material.")
        if not supporting_evidence:
            warnings.append("No direct supporting evidence snippets were found.")

        return {
            "claim": engine_result.get("claim", ""),
            "verdict": engine_result.get("verdict", "unverifiable"),
            "confidence": engine_result.get("confidence", 0.0),
            "evidence_count": engine_result.get("evidence_count", len(supporting_evidence)),
            "supported_count": engine_result.get("supported_count", 0),
            "contradicted_count": engine_result.get("contradicted_count", 0),
            "details": (
                f"Verified against {engine_result.get('evidence_count', 0)} real source text(s); "
                f"{engine_result.get('supported_count', 0)} showed strong support."
            ),
            "supporting_evidence": supporting_evidence,
            "contradictions": engine_result.get("contradictions", []),
            "warnings": warnings,
            "source_results": source_results,
        }

    def _summarize_evidence_usage(self, verification_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        evidence_ids = {
            evidence.get("id")
            for result in verification_results
            for evidence in result.get("supporting_evidence", [])
            if evidence.get("id")
        }
        return {
            "unique_evidence_used": len(evidence_ids),
            "claims_with_evidence": sum(1 for r in verification_results if r.get("supporting_evidence")),
            "low_confidence_claims": sum(1 for r in verification_results if r.get("confidence", 0.0) < 0.5),
        }

    def _build_verification_summary(
        self, 
        verification_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build a user-friendly summary of verification results.
        """
        if not verification_results:
            return {
                "total_claims": 0,
                "supported_claims": 0,
                "partially_supported_claims": 0,
                "contradicted_claims": 0,
                "unsupported_claims": 0,
                "confidence_average": 0.0,
                "issues_found": 0,
                "recommendation": "No claims to verify",
            }
            
        total_claims = len(verification_results)
        supported = sum(1 for r in verification_results if r["verdict"] in ["supported", "partially_supported"])
        contradicted = sum(1 for r in verification_results if r["verdict"] == "contradicted")
        unsupported = sum(1 for r in verification_results if r["verdict"] == "unsupported")
        
        # Calculate average confidence
        confidences = [r["confidence"] for r in verification_results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Compile issues
        issues = []
        for result in verification_results:
            if result.get("warnings"):
                issues.extend(result["warnings"])
            if result.get("contradictions"):
                issues.extend([c["detail"] for c in result["contradictions"]])
                
        # Determine recommendation
        if contradicted > 0:
            recommendation = "Review contradictory claims before publishing"
        elif unsupported > 0:
            recommendation = "Address unsupported claims with additional evidence"
        elif avg_confidence < 0.7:
            recommendation = "Consider strengthening weakly-supported claims"
        else:
            recommendation = "Claims appear well-supported"
            
        return {
            "total_claims": total_claims,
            "supported_claims": supported,
            "partially_supported_claims": sum(1 for r in verification_results 
                                            if r["verdict"] == "partially_supported"),
            "contradicted_claims": contradicted,
            "unsupported_claims": unsupported,
            "confidence_average": round(avg_confidence, 3),
            "issues_found": len(issues),
            "recommendation": recommendation,
        }

    def get_claim_feedback(
        self, 
        claim: str, 
        verification_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get detailed feedback for a single claim.
        
        Args:
            claim: The claim text
            verification_result: Verification result for this claim
            
        Returns:
            Detailed feedback for UI display
        """
        feedback = {
            "claim": claim,
            "verdict": verification_result.get("verdict", "unknown"),
            "confidence": verification_result.get("confidence", 0.0),
            "status_color": self._get_verdict_color(verification_result.get("verdict")),
            "status_label": self._get_verdict_label(verification_result.get("verdict")),
            "supporting_evidence": verification_result.get("supporting_evidence", []),
            "contradictions": verification_result.get("contradictions", []),
            "warnings": verification_result.get("warnings", []),
            "details": verification_result.get("details", ""),
        }
        
        return feedback

    def _get_verdict_color(self, verdict: str) -> str:
        """Get color code for verdict for UI display."""
        color_map = {
            "supported": "green",
            "partially_supported": "yellow",
            "contradicted": "red",
            "unsupported": "orange",
            "unverifiable": "gray",
        }
        return color_map.get(verdict, "gray")

    def _get_verdict_label(self, verdict: str) -> str:
        """Get human-readable label for verdict."""
        label_map = {
            "supported": "Well-supported",
            "partially_supported": "Partially supported",
            "contradicted": "Contradicted",
            "unsupported": "Unsupported",
            "unverifiable": "Unverifiable",
        }
        return label_map.get(verdict, "Unknown")


# Global instance
verification_ui = VerificationUX()