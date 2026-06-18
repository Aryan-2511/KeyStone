"""LLM edge — extraction, summarization, NL interaction, and the inference switch.

Where models live. Selected by config (hosted NIM = demo, local Ollama =
production) on one code path. The core must not depend on it.
"""

from __future__ import annotations

from .phrasing import phrase_summary

__all__ = ["phrase_summary"]
