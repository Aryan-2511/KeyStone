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
# v4 (M1-06): added the `matrix` block (the characterized seam-matrix result).
# v5 (M2-0n): added the `convergence` block (the regulatory-convergence result).
# v6 (MA-01): added the `red_team` block (the Red-Team Agent's recorded decision trace).
RUN_RESULT_SCHEMA_VERSION = 6


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


class MatrixPairView(BaseModel):
    """One (attack, financial-crime) pair in the characterized seam matrix (M1-06).

    Derived from `keystone.assurance.pairs.REGISTERED_PAIRS` — never hardcoded. Carries
    the mapping a reviewer reads off the figure: the attack class (OWASP id + plain
    name), the FATF typology it binds to (plain name + label, or None for the boundary),
    the result, and the axis grouping (A = vary the typology, hold the attack class;
    B = vary the attack class — the anti-cherry-pick sampling).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    pair_id: str
    attack_owasp_id: str
    attack_name: str
    # The FATF typology this pair binds to, or None for the BOUNDARY pair (no typology).
    typology: str | None
    typology_label: str
    result: str  # "CLEAN" | "BOUNDARY"
    axis: str  # "A" | "B"


class MatrixView(BaseModel):
    """The characterized seam-matrix result (M1-06) — the paper's central figure.

    The whole matrix as a single derived artifact: the per-pair mapping, the result
    distribution, the boundary statement (P4), and the ONE independence property the
    shared framework carries (stated once, not per pair). All derived from
    `REGISTERED_PAIRS` so adding a pair appears here with nothing hardcoded.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    pairs: tuple[MatrixPairView, ...]
    clean_count: int
    boundary_count: int
    boundary_statement: str
    independence_property: str


class ConvergenceMappingView(BaseModel):
    """One seam-event → obligation evidence relationship (M2-0n), for the hero.

    Derived from `keystone.convergence.REGISTERED_MAPPINGS` — never hardcoded. Carries
    the four-part rigor a reviewer reads (obligation + requirement + reason), the
    enforcement modality, and — for EVIDENCED mappings — the VIOLATE→SATISFY states with
    the before/after numbers that CAUSE the flip. `kind` is EVIDENCED or NOT_EVIDENCED
    (the DPDP boundary). For the boundary the states/numbers are None.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    obligation_id: str
    obligation_label: str
    jurisdiction: str
    modality: str  # "HARD_LAW" | "SELF_CERTIFICATION"
    modality_label: str  # plain language: "hard law" | "advisory"
    requirement: str
    reason: str
    kind: str  # "EVIDENCED" | "NOT_EVIDENCED"
    # The temporal state-flip — None for the boundary (no satisfy/violate state).
    pre_state: str | None  # "VIOLATE"
    post_state: str | None  # "SATISFY"
    before_fails: int | None
    after_fails: int | None
    prompt_cap: int | None


class ConvergenceView(BaseModel):
    """The regulatory-convergence result (M2-0n) — the loop made visible.

    The whole evidence set as a derived artifact: per-mapping the obligation it
    evidences (violated→satisfied, or the boundary), the cross-jurisdiction modality
    spread, and the honest `disclaimer`. All derived from `REGISTERED_MAPPINGS` so
    adding a mapping appears here with nothing hardcoded.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    mappings: tuple[ConvergenceMappingView, ...]
    evidenced_count: int
    boundary_count: int
    hard_law_count: int
    advisory_count: int
    jurisdictions: tuple[str, ...]
    disclaimer: str


class RedTeamProbeView(BaseModel):
    """One step of the Red-Team Agent's decision trace (MA-01), for the UI.

    The (observed-outcomes → chosen-probe) step the agent actually took: the probe it
    chose, the phase (scout / exploit), why (the observation-driven rationale), and
    the outcome it then observed. Derived from a genuine `keystone.agents.red_team`
    run — never hand-authored.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    step: int
    phase: str  # "scout" | "exploit"
    family: str
    probe: str
    rationale: str
    fails: int
    total_evaluated: int
    failure_rate: float
    got_through: bool


class RedTeamView(BaseModel):
    """The Red-Team Agent's recorded decision trace (MA-01) — the agentic offense.

    DERIVED from a genuine `keystone.agents.red_team` run: the ordered
    (observed-outcomes → chosen-probe) steps, replayed deterministically offline
    (MA-00 §4). The agent is honest by MA-00 §2 — its sequence is a function of what
    it observed, not a fixed list — and honestly named by MA-00 §3: `mechanism`
    states it is an adaptive policy, NOT an LLM. `families_available` is the real
    Garak decision space; `exploited_family` / `abandoned_families` are what the
    agent did with it on this run's observed defense.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    decisions: tuple[RedTeamProbeView, ...]
    probe_sequence: tuple[str, ...]
    families_available: tuple[str, ...]
    scouted_families: tuple[str, ...]
    exploited_family: str | None
    abandoned_families: tuple[str, ...]
    probes_run: int
    mechanism: str


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
    # The characterized seam-matrix result (M1-06) — derived from REGISTERED_PAIRS.
    matrix: MatrixView
    # The regulatory-convergence result (M2-0n) — derived from REGISTERED_MAPPINGS.
    convergence: ConvergenceView
    # The Red-Team Agent's recorded decision trace (MA-01) — a genuine agentic run.
    red_team: RedTeamView
