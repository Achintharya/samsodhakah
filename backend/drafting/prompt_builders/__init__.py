"""
Prompt Builders — modular prompt construction for grounded drafting.
"""

from __future__ import annotations
from backend.drafting.prompt_builders.related_work import build_related_work_prompt
from backend.drafting.prompt_builders.methodology import build_methodology_prompt
from backend.drafting.prompt_builders.results import build_results_prompt
from backend.drafting.prompt_builders.discussion import build_discussion_prompt
from backend.drafting.prompt_builders.abstract import build_abstract_prompt

__all__ = [
    "build_related_work_prompt",
    "build_methodology_prompt",
    "build_results_prompt",
    "build_discussion_prompt",
    "build_abstract_prompt"
]