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
from .garak_probe import (
    CURATED_PROBES,
    FAMILY_MAPPINGS,
    PINNED_GARAK_VERSION,
    PROMPT_INJECTION_FAMILIES,
    GarakError,
    GarakFinding,
    GarakMappingError,
    MappedFinding,
    RegulatoryMapping,
    ScanConfig,
    found_our_vulnerability,
    map_finding,
    parse_report,
    record_finding,
    run_scan,
    scan_mock_agent,
)
from .referenced import REFERENCED_ASSURANCE, ReferencedAssurance
from .seam import (
    SeamError,
    SeamProof,
    prove_seam,
    resolve_signature,
    seam_fraud_stream,
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
    "CURATED_PROBES",
    "FAMILY_MAPPINGS",
    "LAYER",
    "LEDGER_ACTION",
    "MEMO_INJECTION_SIGNATURE",
    "PINNED_GARAK_VERSION",
    "REFERENCED_ASSURANCE",
    "ReferencedAssurance",
    "PROMPT_INJECTION_FAMILIES",
    "TOOLS",
    "VULNERABLE_SYSTEM_PROMPT",
    "AgentRun",
    "ExploitOutcome",
    "GarakError",
    "GarakFinding",
    "GarakMappingError",
    "InjectionField",
    "InjectionMechanism",
    "MaliciousMemoExample",
    "MappedFinding",
    "RegulatoryMapping",
    "ScanConfig",
    "SeamError",
    "SeamProof",
    "Transaction",
    "TransferIntent",
    "VulnerabilitySignature",
    "exploit_fired",
    "found_our_vulnerability",
    "map_finding",
    "parse_report",
    "prove_seam",
    "record_finding",
    "resolve_signature",
    "run_agent",
    "run_scan",
    "seam_fraud_stream",
    "scan_mock_agent",
]
