"""
Prompt Builder — generates grounded prompts for Methodology sections.
"""

from __future__ import annotations
from typing import Dict, List
from backend.utils.token_metrics import token_metrics

def build_methodology_prompt(
    topic: str,
    evidence_units: List[Dict],
    citations: List[Dict],
    max_tokens: int = 2048
) -> str:
    """
    Build a grounded prompt for Methodology sections.

    Args:
        topic: Research topic
        evidence_units: List of evidence units with methodology details
        citations: List of citation references
        max_tokens: Maximum token limit for prompt

    Returns:
        Grounded prompt string
    """
    # Build prompt components
    prompt_components = [
        f"Research Topic: {topic}\n\n",
        "Methodological Evidence:\n"
    ]

    # Add evidence with methodology details
    for i, ev in enumerate(evidence_units[:5]):
        if ev.get("unit_type") in ["methodology", "experimental_setup"]:
            prompt_components.append(
                f"{i+1}. {ev.get('content', '')[:200]}...\n"
                f"   Source: {ev.get('source_document_id', 'Unknown')}\n"
                f"   Type: {ev.get('unit_type', 'methodology')}\n"
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
    Generate a comprehensive Methodology section that:
    1. Describes the research approach
    2. Details experimental design and procedures
    3. Explains data collection methods
    4. Justifies choices with evidence from provided sources
    5. Maintains academic rigor and proper citations

    Structure your response with:
    - Introduction to the methodology
    - Detailed description of methods/techniques
    - Data collection and analysis procedures
    - Justification of methodological choices
    - Limitations and potential biases
    - Conclusion summarizing the approach
    """)

    # Combine components
    prompt = "\n".join(prompt_components)

    # Log token usage
    token_metrics.log(
        operation="prompt_building",
        subsystem="methodology",
        input_tokens=len(prompt) // 4,
        metadata={
            "topic": topic,
            "evidence_count": len(evidence_units),
            "citation_count": len(citations)
        }
    )

    return prompt