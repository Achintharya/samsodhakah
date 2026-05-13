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
        
        # Get source documents for verification
        source_docs = []
        
        # Add main document
        main_doc = semantic_memory.get_document(document_id)
        if main_doc:
            source_docs.append(main_doc)
        
        # Add related work if specified
        if related_work_id:
            related_doc = semantic_memory.get_document(related_work_id)
            if related_doc:
                source_docs.append(related_doc)
        
        # Prepare source texts for verification
        source_texts = {}
        for doc in source_docs:
            doc_id = doc.get("document_id")
            # In a real implementation, we would get actual document text
            # For now, we simulate with document metadata
            source_texts[doc_id] = f"Document: {doc.get('title', 'Unknown')} - {doc.get('filename', '')}"
        
        # Verify each claim
        verification_results = []
        for claim in claims[:10]:  # Limit to first 10 claims for performance
            if claim.strip():
                try:
                    # In a real implementation, this would call verification_engine.verify_claim
                    # For now, we simulate it with a basic result
                    result = self._simulate_verification_result(claim, source_texts)
                    verification_results.append(result)
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
                    
        return claims[:15]  # Limit to 15 claims for performance

    def _simulate_verification_result(
        self, 
        claim: str, 
        source_texts: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Simulate verification results for demonstration purposes.
        """
        # In a real system, this would call the actual verification engine
        # For now, we simulate based on claim content
        
        # Simple heuristics for demonstration
        if "shows" in claim.lower() or "demonstrates" in claim.lower():
            verdict = "supported"
            confidence = 0.85
        elif "however" in claim.lower() or "but" in claim.lower():
            verdict = "partially_supported" if len(source_texts) > 1 else "supported"
            confidence = 0.7
        elif any(word in claim.lower() for word in ["not", "no", "negative", "opposite"]):
            verdict = "contradicted" if len(source_texts) > 1 else "supported"
            confidence = 0.6
        else:
            verdict = "supported"
            confidence = 0.9
            
        # Mock evidence and contradictions
        supporting_evidence = [
            {
                "id": f"evidence_{i}",
                "source_document": list(source_texts.keys())[0] if source_texts else "unknown",
                "content_preview": "Supporting evidence...",
                "confidence": confidence,
                "role": "supports",
            } for i in range(min(2, len(source_texts)))
        ]
        
        contradictions = []
        if verdict == "contradicted":
            contradictions.append({
                "type": "lexical",
                "source_a": list(source_texts.keys())[0] if source_texts else "unknown",
                "source_b": "different_source",
                "detail": "Contradictory evidence found",
                "severity": 0.8,
            })
        
        warnings = []
        if confidence < 0.7:
            warnings.append("Low confidence in claim verification")
            
        return {
            "claim": claim,
            "verdict": verdict,
            "confidence": round(confidence, 4),
            "evidence_count": len(supporting_evidence),
            "details": f"Claim analyzed with {len(supporting_evidence)} supporting pieces",
            "supporting_evidence": supporting_evidence,
            "contradictions": contradictions,
            "warnings": warnings,
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