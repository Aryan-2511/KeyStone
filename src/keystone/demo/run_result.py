"""The typed, serializable run-result — the UI's contract over the Layer-1 arc.

This is a typed VIEW over the system of record (the hash-chained evidence ledger),
not a new source of truth. One `RunResult` captures everything the Phase-5
front-end (KS-0501 seam hero, KS-0502 jurisdiction hero, KS-0503 supporting shell)
renders for a single end-to-end run:

- the seam TRANSACTION at the visual centre (real id, amount, accounts, memo);
- the Layer-1 FINANCIAL-CRIME finding (FATF, memo-blind);
- the Layer-2 AI-SECURITY vulnerability (the canonical signature + its OWASP /
  regulatory mapping) — REFERENCED by signature identity, never re-run here;
- the BINDING (the shared transaction id + the canonical signature) — the thesis;
- the FINnet report (facts + guarded narrative + sign-off);
- the ordered, hash-valid ARC (the ledger entries + chain-integrity summary).

Every field is populated by `keystone.demo.runner.build_run_result` from a real
arc run over the seeded synthetic stream — no placeholder data. The model is
frozen and round-trips through JSON (`model_dump_json` / `model_validate_json`)
so a saved run replays identically offline.

Boundary: lives in `keystone.demo` (the integration/demo layer) because it draws
from both the deterministic core (transactions, FATF, reporting, ledger) and the
assurance edge (the seam signature + regulatory mapping); the core never imports
it (import-linter KEPT).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from keystone.core.ledger import LedgerEntry

# Schema version for the on-disk run-result; bump on any breaking shape change so
# a saved run that no longer matches fails loudly rather than rendering wrong.
RUN_RESULT_SCHEMA_VERSION = 3


class SeamTransactionView(BaseModel):
    """The ONE transaction at the visual centre — the object both findings bind to."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    timestamp: str
    sender_account: str
    recipient_account: str
    amount: float
    currency: str
    tx_type: str
    memo: str


class FinancialCrimeView(BaseModel):
    """Layer-1 side: the memo-blind FATF finding (financial-crime grounds only)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    layer: str
    typology: str
    severity: str
    account: str
    transaction_ids: tuple[str, ...]
    signal: dict[str, object]
    rationale: str


class RegulatoryMappingView(BaseModel):
    """The vulnerability's OWASP + cross-jurisdiction regulatory context.

    Imported verbatim from the curated assurance mapping (KS-0303) — feeds both the
    seam hero's L2 label and the KS-0502 jurisdiction-contrast screen.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    owasp_llm: str
    owasp_agentic: str
    eu_ai_act: str
    eu_obligation_id: str
    # The EU obligation's enforcement modality from the obligation graph — HARD_LAW
    # (binding, fineable). The KS-0502 contrast reads this, never assumes it.
    eu_modality: str
    india_principle: str
    india_obligation_id: str
    # The India obligation's modality — SELF_CERTIFICATION (advisory, principle-based:
    # RBI FREE-AI / DPDP / MeitY). A different governance choice, not a lesser one.
    india_modality: str


class AssuranceView(BaseModel):
    """The referenced L2 find-and-patch result (KS-0304) — the before/after proof.

    Carried from the canonical `REFERENCED_ASSURANCE` constant (referenced, not re-run):
    `before_fails`/`prompt_cap` probes exploited the unguarded agent; `after_fails`
    once the Guardrails rail was added. The KS-0503 before/after view renders this.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    prompt_cap: int
    before_fails: int
    after_fails: int
    exploit_before: bool
    exploit_after: bool
    remediated: bool
    found_by: str
    patched_by: str


class AiSecurityView(BaseModel):
    """Layer-2 side: the prompt-injection vulnerability, REFERENCED not re-run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    layer: str
    signature_name: str
    field: str
    mechanism: str
    outcome: str
    exploit_tool: str
    description: str
    # How the seam cites the already-proven L2 finding (Garak found, Guardrails
    # patched) — referenced by signature identity, not re-run in this arc.
    l2_reference: str
    regulatory: RegulatoryMappingView
    assurance: AssuranceView


class SeamBindingView(BaseModel):
    """The signature element: both findings bind to the SAME tx id + SAME signature."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    transaction_id: str
    signature_name: str
    fatf_typology: str
    thesis: str


class ReportView(BaseModel):
    """The drafted, signed-off STR — its summary plus BOTH regulator renderings.

    `finnet` (FIU-IND, India) and `goaml` (UN goAML, 70+ countries) are the SAME
    facts rendered into two formats: the "one fact model, many connectors" claim the
    KS-0502 screen makes literal. Both are produced by `keystone.core.reporting`
    adapters over one `Report`, so they cannot drift from each other.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    report_format: str
    status: str
    signed_by: str
    narrative: str
    narrative_fell_back: bool
    currency: str
    total_amount: float
    transaction_count: int
    period_start: str
    period_end: str
    finnet: dict[str, object]
    goaml: dict[str, object]


class ArcView(BaseModel):
    """Posture: the ordered arc, its chain integrity, and the evidence entries.

    Carries the full ledger entries so a saved run replays the whole evidence trail
    (and re-verifies the hash chain) offline — the KS-0503 shell / KS-0504 fallback.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    stages: tuple[str, ...]
    arc_complete: bool
    chain_verified: bool
    entries: tuple[LedgerEntry, ...]

    @property
    def entry_count(self) -> int:
        return len(self.entries)


class RunResult(BaseModel):
    """One end-to-end Layer-1 run, as the typed object the front-end renders."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int
    generated_at: str
    seam_transaction: SeamTransactionView
    financial_crime: FinancialCrimeView
    ai_security: AiSecurityView
    binding: SeamBindingView
    report: ReportView
    arc: ArcView
