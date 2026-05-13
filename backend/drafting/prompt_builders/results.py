"""
Prompt Builder — generates grounded prompts for Results sections.
"""

from __future__ import annotations
from typing import Dict, List
from backend.utils.token_metrics import token_metrics

def build_results_prompt(
    topic: str,
    evidence_units: List[Dict],
    citations: List[Dict],
    max_tokens: int = 2048
) -> str:
    """
    Build a grounded prompt for Results sections.

    Args:
        topic: Research topic
        evidence_units: List of evidence units with experimental results
        citations: List of citation references
        max_tokens: Maximum token limit for prompt

    Returns:
        Grounded prompt string
    """
    # Build prompt components
    prompt_components = [
        f"Research Topic: {topic}\n\n",
        "Experimental Results Evidence:\n"
    ]

    # Add evidence with results details
    for i, ev in enumerate(evidence_units[:5]):
        if ev.get("unit_type") in ["experimental_result", "metric"]:
            prompt_components.append(
                f"{i+1}. {ev.get('content', '')[:200]}...\n"
                f"   Source: {ev.get('source_document_id', 'Unknown')}\n"
                f"   Type: {ev.get('unit_type', 'experimental_result')}\n"
                f"   Confidence: {ev.get('confidence', 0.0):.2f}\n"
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
    Generate a comprehensive Results section that:
    1. Presents experimental findings clearly
    2. Uses evidence from provided sources
    3. Includes quantitative data and analysis
    4. Discusses statistical significance where applicable
    5. Maintains academic tone and proper citations

    Structure your response with:
    - Introduction to the results
    - Detailed presentation of findings
    - Analysis and interpretation
    - Statistical significance (if applicable)
    - Visualization of key results
    - Conclusion summarizing the outcomes
    """)

    # Combine components
    prompt = "\n".join(prompt_components)

    # Log token usage
    token_metrics.log(
        operation="prompt_building",
        subsystem="results",
        input_tokens=len(prompt) // 4,
        metadata={
            "topic": topic,
            "evidence_count": len(evidence_units),
            "citation_count": len(citations)
        }
    )

    return prompt