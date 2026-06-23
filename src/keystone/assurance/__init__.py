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
from .framework import (
    AttackChannel,
    AttackSide,
    CrimeSide,
    FinancialProjection,
    PairBinding,
    SeamDriftError,
    SeamEvent,
    SeamPair,
    SeamResult,
    bind,
    financial_projection_for,
    project_financial,
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
from .pairs import REGISTERED_PAIRS
from .referenced import REFERENCED_ASSURANCE, ReferencedAssurance
from .seam import (
    P1_PAIR,
    SeamError,
    SeamProof,
    prove_seam,
    resolve_signature,
    seam_fraud_stream,
)
from .seam_p2 import (
    P2_PAIR,
    p2_fraud_stream,
    resolve_forwarding_signature,
)
from .signature import (
    CANONICAL_FORWARDING_EXPLOIT,
    CANONICAL_MEMO_EXPLOIT,
    MEMO_FORWARDING_SIGNATURE,
    MEMO_INJECTION_SIGNATURE,
    ExploitOutcome,
    InjectionField,
    InjectionMechanism,
    MaliciousMemoExample,
    VulnerabilitySignature,
)

__all__ = [
    "AGENT_NAME",
    "CANONICAL_FORWARDING_EXPLOIT",
    "CANONICAL_MEMO_EXPLOIT",
    "CURATED_PROBES",
    "FAMILY_MAPPINGS",
    "LAYER",
    "LEDGER_ACTION",
    "MEMO_FORWARDING_SIGNATURE",
    "MEMO_INJECTION_SIGNATURE",
    "P1_PAIR",
    "P2_PAIR",
    "PINNED_GARAK_VERSION",
    "REFERENCED_ASSURANCE",
    "REGISTERED_PAIRS",
    "ReferencedAssurance",
    "PROMPT_INJECTION_FAMILIES",
    "TOOLS",
    "VULNERABLE_SYSTEM_PROMPT",
    "AgentRun",
    "AttackChannel",
    "AttackSide",
    "CrimeSide",
    "ExploitOutcome",
    "FinancialProjection",
    "GarakError",
    "GarakFinding",
    "GarakMappingError",
    "InjectionField",
    "InjectionMechanism",
    "MaliciousMemoExample",
    "MappedFinding",
    "PairBinding",
    "RegulatoryMapping",
    "ScanConfig",
    "SeamDriftError",
    "SeamError",
    "SeamEvent",
    "SeamPair",
    "SeamProof",
    "SeamResult",
    "Transaction",
    "TransferIntent",
    "VulnerabilitySignature",
    "bind",
    "exploit_fired",
    "financial_projection_for",
    "found_our_vulnerability",
    "map_finding",
    "p2_fraud_stream",
    "parse_report",
    "project_financial",
    "prove_seam",
    "record_finding",
    "resolve_forwarding_signature",
    "resolve_signature",
    "run_agent",
    "run_scan",
    "seam_fraud_stream",
    "scan_mock_agent",
]
