"""
Prompt Builder — generates grounded prompts for Discussion sections.
"""

from __future__ import annotations
from typing import Dict, List
from backend.utils.token_metrics import token_metrics

def build_discussion_prompt(
    topic: str,
    evidence_units: List[Dict],
    citations: List[Dict],
    max_tokens: int = 2048
) -> str:
    """
    Build a grounded prompt for Discussion sections.

    Args:
        topic: Research topic
        evidence_units: List of evidence units with discussion points
        citations: List of citation references
        max_tokens: Maximum token limit for prompt

    Returns:
        Grounded prompt string
    """
    # Build prompt components
    prompt_components = [
        f"Research Topic: {topic}\n\n",
        "Discussion Evidence:\n"
    ]

    # Add evidence with discussion points
    for i, ev in enumerate(evidence_units[:5]):
        if ev.get("unit_type") in ["discussion", "limitation", "interpretation"]:
            prompt_components.append(
                f"{i+1}. {ev.get('content', '')[:200]}...\n"
                f"   Source: {ev.get('source_document_id', 'Unknown')}\n"
                f"   Type: {ev.get('unit_type', 'discussion')}\n"
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
    Generate a comprehensive Discussion section that:
    1. Interprets the results in context
    2. Discusses implications of findings
    3. Compares with related work
    4. Identifies limitations and biases
    5. Suggests future research directions
    6. Maintains academic tone and proper citations

    Structure your response with:
    - Interpretation of results
    - Comparison with related work
    - Discussion of implications
    - Identification of limitations
    - Suggestions for future work
    - Conclusion summarizing the discussion
    """)

    # Combine components
    prompt = "\n".join(prompt_components)

    # Log token usage
    token_metrics.log(
        operation="prompt_building",
        subsystem="discussion",
        input_tokens=len(prompt) // 4,
        metadata={
            "topic": topic,
            "evidence_count": len(evidence_units),
            "citation_count": len(citations)
        }
    )

    return prompt