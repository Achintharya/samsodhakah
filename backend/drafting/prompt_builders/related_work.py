"""
Prompt Builder — generates grounded prompts for Related Work sections.
"""

from __future__ import annotations
from typing import Dict, List
from backend.utils.token_metrics import token_metrics

def build_related_work_prompt(
    topic: str,
    evidence_units: List[Dict],
    citations: List[Dict],
    max_tokens: int = 2048
) -> str:
    """
    Build a grounded prompt for Related Work sections.

    Args:
        topic: Research topic
        evidence_units: List of evidence units with citations
        citations: List of citation references
        max_tokens: Maximum token limit for prompt

    Returns:
        Grounded prompt string
    """
    # Calculate token usage for evidence
    evidence_tokens = sum(len(ev.get("content", "")) for ev in evidence_units[:5])
    citation_tokens = sum(len(cit.get("content", "")) for cit in citations[:3])

    # Build prompt components
    prompt_components = [
        f"Research Topic: {topic}\n\n",
        "Relevant Evidence:\n"
    ]

    # Add evidence with citations
    for i, ev in enumerate(evidence_units[:5]):
        prompt_components.append(
            f"{i+1}. {ev.get('content', '')[:200]}...\n"
            f"   Source: {ev.get('source_document_id', 'Unknown')}\n"
            f"   Role: {ev.get('role', 'supports')}\n"
        )

    # Add citations
    prompt_components.append("\nCitations:\n")
    for i, cit in enumerate(citations[:3]):
        prompt_components.append(
            f"{i+1}. {cit.get('content_preview', '')[:150]}...\n"
            f"   Source: {cit.get('source_document', 'Unknown')}\n"
        )

    # Add grounding instructions
    prompt_components.append("""
    Generate a comprehensive Related Work section that:
    1. Summarizes key prior research
    2. Highlights contributions of related work
    3. Identifies gaps in current understanding
    4. Positions this work in the broader context
    5. Uses evidence from the provided sources
    6. Maintains academic tone and proper citations

    Structure your response with:
    - Introduction to the research area
    - Key related works (with citations)
    - Gaps and limitations
    - How this work addresses those gaps
    - Conclusion summarizing the context
    """)

    # Combine components
    prompt = "\n".join(prompt_components)

    # Log token usage
    token_metrics.log(
        operation="prompt_building",
        subsystem="related_work",
        input_tokens=len(prompt) // 4,
        metadata={
            "topic": topic,
            "evidence_count": len(evidence_units),
            "citation_count": len(citations)
        }
    )

    return prompt