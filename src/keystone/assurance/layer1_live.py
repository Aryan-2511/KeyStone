"""Live wiring for the Layer-1 milestone (KS-0405).

Kept separate from `layer1_milestone.py` so the spine + its fast tests stay free of
the live backend — the only live stage is the guarded narrative (the LLM edge).
"""

from __future__ import annotations

from keystone.core.reporting import ReportFacts
from keystone.llm.inference import OllamaBackend
from keystone.llm.report_narrative import GuardedNarrative, generate_narrative


def live_narrate(facts: ReportFacts) -> GuardedNarrative:
    """Generate the report narrative on the live backend (Ollama qwen2.5:3b)."""
    return generate_narrative(facts, backend=OllamaBackend())
