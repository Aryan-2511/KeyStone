"""Assurance / red-team scaffolding — the Layer-2 AI Assurance Loop.

Home of the mock vulnerable payments agent (KS-0301) that Garak probes and
Guardrails will patch, plus the canonical vulnerability SIGNATURE that the future
Garak probe (KS-0303) and the Layer-1 fraud fixture (KS-0403) both import — one
source of truth for the planted flaw. Later, the in-repo driver that invokes Garak
as an external subprocess (ADR-0003) lives here too.

This layer may depend on the core and the LLM edge; the core never imports it.
"""

from __future__ import annotations

from .agent import (
    AGENT_NAME,
    LAYER,
    LEDGER_ACTION,
    TOOLS,
    VULNERABLE_SYSTEM_PROMPT,
    AgentRun,
    Transaction,
    TransferIntent,
    exploit_fired,
    run_agent,
)
from .signature import (
    CANONICAL_MEMO_EXPLOIT,
    MEMO_INJECTION_SIGNATURE,
    ExploitOutcome,
    InjectionField,
    InjectionMechanism,
    MaliciousMemoExample,
    VulnerabilitySignature,
)

__all__ = [
    "AGENT_NAME",
    "CANONICAL_MEMO_EXPLOIT",
    "LAYER",
    "LEDGER_ACTION",
    "MEMO_INJECTION_SIGNATURE",
    "TOOLS",
    "VULNERABLE_SYSTEM_PROMPT",
    "AgentRun",
    "ExploitOutcome",
    "InjectionField",
    "InjectionMechanism",
    "MaliciousMemoExample",
    "Transaction",
    "TransferIntent",
    "VulnerabilitySignature",
    "exploit_fired",
    "run_agent",
]
