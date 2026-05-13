"""
Prompt Builder — generates grounded prompts for Abstract sections.
"""

from __future__ import annotations
from typing import Dict, List
from backend.utils.token_metrics import token_metrics

def build_abstract_prompt(
    topic: str,
    evidence_units: List[Dict],
    citations: List[Dict],
    max_tokens: int = 1024
) -> str:
    """
    Build a grounded prompt for Abstract sections.

    Args:
        topic: Research topic
        evidence_units: List of evidence units with abstract-relevant information
        citations: List of citation references
        max_tokens: Maximum token limit for prompt

    Returns:
        Grounded prompt string
    """
    # Build prompt components
    prompt_components = [
        f"Research Topic: {topic}\n\n",
        "Abstract Evidence:\n"
    ]

    # Add evidence with abstract-relevant information
    for i, ev in enumerate(evidence_units[:3]):
        prompt_components.append(
            f"{i+1}. {ev.get('content', '')[:150]}...\n"
            f"   Source: {ev.get('source_document_id', 'Unknown')}\n"
            f"   Role: {ev.get('role', 'supports')}\n"
        )

    # Add citations
    prompt_components.append("\nCitations:\n")
    for i, cit in enumerate(citations[:2]):
        prompt_components.append(
            f"{i+1}. {cit.get('content_preview', '')[:100]}...\n"
            f"   Source: {cit.get('source_document', 'Unknown')}\n"
        )

    # Add grounding instructions
    prompt_components.append("""
    Generate a concise Abstract section that:
    1. Clearly states the research problem
    2. Summarizes key contributions
    3. Describes the methodology
    4. Highlights main results
    5. Provides implications
    6. Maintains academic tone and proper citations

    Structure your response with:
    - Research problem statement
    - Key contributions
    - Methodology summary
    - Main results
    - Implications and significance
    - Conclusion
    """)

    # Combine components
    prompt = "\n".join(prompt_components)

    # Log token usage
    token_metrics.log(
        operation="prompt_building",
        subsystem="abstract",
        input_tokens=len(prompt) // 4,
        metadata={
            "topic": topic,
            "evidence_count": len(evidence_units),
            "citation_count": len(citations)
        }
    )

    return prompt