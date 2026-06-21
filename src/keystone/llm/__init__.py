"""LLM edge — extraction, summarization, NL interaction, and the inference switch.

Where models live. Selected by config (hosted NIM = demo, local Ollama =
production) on one code path. The core must not depend on it.
"""

from __future__ import annotations

from .phrasing import PhrasedSummary, phrase_summary
from .report_narrative import GuardedNarrative, draft_report, generate_narrative

__all__ = [
    "GuardedNarrative",
    "PhrasedSummary",
    "draft_report",
    "generate_narrative",
    "phrase_summary",
]
