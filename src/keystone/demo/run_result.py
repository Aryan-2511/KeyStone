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
# v7 (MB-01): added the `triage` block (the Triage Agent's recorded routing decision).
RUN_RESULT_SCHEMA_VERSION = 7


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
    agent did with it on this run's observed defense. ``source`` records WHERE the
    outcomes came from (OPT-A-02): the recorded profile by default, or ``garak_live``
    for a real Garak scan run with ``--live``; a fallback is never reported as live.
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
    # WHERE the outcomes came from (OPT-A-02, the honesty guarantee): "recorded_profile"
    # (offline default / live fallback) or "garak_live" (real Garak scans). Defaults to
    # the recorded profile so a run recorded before live mode existed — which genuinely
    # WAS a recorded-profile run — stays truthfully labelled and still loads (no bump).
    source: str = "recorded_profile"
    # WHICH probe set the run scanned (OPT-A-02b): "full" (offline recorded / the opt-in
    # --deep live run) or "tractable" (the default live scan — the known-intractable deep
    # probes excluded, so a real scan is bounded to minutes). Defaults to "full" so a run
    # recorded before scoping existed — the whole catalog was available — stays truthful
    # and still loads (no schema bump). Mirrors red_team.SCOPE_FULL / SCOPE_TRACTABLE.
    scan_scope: str = "full"


class TriageView(BaseModel):
    """The Triage Agent's recorded routing decision (MB-01) — the supervisor's call.

    DERIVED by actually RUNNING the Triage Agent (`keystone.agents.triage.triage`)
    over the finding's already-computed signals — never hand-authored. The supervisor
    reads the offense worker's strongest landed exploit (`failure_rate`), the seam's
    classification (`seam_result`), and the mapped `severity`, and routes the finding
    to one of `routes_available` (the genuine 3-option space). The route depends on the
    INTERPLAY of the three signals, not a single threshold (the MB-00 §2 honesty test):
    `rationale` states which signals were decisive. `reasoner` records WHICH reasoner
    produced the route (OPT-A-01): the transparent policy by default, or a live LLM when
    run with `--live`; `mechanism` is the matching human label. We never report a policy
    fallback as an LLM decision. "remediate" is a ROUTE (this finding warrants
    remediation), not a choice among fixes (gated Movement C, §6).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    route: str  # "remediate" | "accept" | "escalate"
    # The already-computed signals the agent saw (read-only; it never recomputed them).
    failure_rate: float
    seam_result: str  # "clean" | "boundary" | "open"
    severity: str  # "LOW" | "MEDIUM" | "HIGH"
    rationale: str
    # The policy's noise floor (transparency — below this, nothing is actionable).
    action_floor: float
    # The genuine 3-option action space — each route reachable (no agency-theater).
    routes_available: tuple[str, ...]
    mechanism: str
    # WHICH reasoner produced the route (OPT-A-01, the honesty guarantee): "policy"
    # (offline default), "policy_fallback" (live asked, LLM unavailable → policy ran),
    # or "llm:<model>" (a live LLM genuinely reasoned it). Defaults to "policy" so a run
    # recorded before live mode existed — which genuinely WAS a policy run — stays
    # truthfully labelled and still loads (no schema bump: old data is still accurate).
    reasoner: str = "policy"


class DefenseView(BaseModel):
    """The Defense Agent's recorded remediation choice (MC-01) — the defender's call.

    DERIVED by actually RUNNING the Defense Agent (`keystone.agents.defense.defend`) over the
    finding's two-sided strength — never hand-authored. The agent reads the AI-side strength
    (`failure_rate` — the injection's landed rate) and the financial-side `financial_gap` (True
    when a transaction slips baseline detection but tightening catches it), and CHOOSES which
    remediation the finding warrants: `control` names it, `side` is which side of the seam it
    acts on ("ai" = block the prompt / "financial" = tighten the money). The choice is
    finding-dependent (the flip test) and policy-first (`reasoner` = "policy"; NOT an LLM —
    compute-gated, OPT-A-01b). `verified_offline` is honestly asymmetric: True/False for the
    financial-side (an offline detection change) or null for the AI-side (its effect needs the
    MC-02 re-scan); `retest_via` is the loop-ready handle MC-02 would re-test through.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    control: str  # the chosen remediation's control name
    side: str  # "ai" | "financial" — which side of the seam it acts on
    # The two-sided strength the agent saw (read-only; memo-blind).
    failure_rate: float
    financial_gap: bool
    seam_result: str  # "clean" | "boundary" | "open"
    severity: str  # "LOW" | "MEDIUM" | "HIGH"
    rationale: str
    # The genuine ≥2-option menu (each reachable — no dispatch-theater).
    remediations_available: tuple[str, ...]
    mechanism: str
    reasoner: str  # "policy" — defense is policy-first in MC-01 (no LLM)
    # The uniform apply() outcome (MC-00 §2): what the chosen remediation did.
    summary: str
    detail: tuple[str, ...]  # concrete artifacts (e.g. the tx ids (c) newly covers)
    retest_via: str  # the handle MC-02's adversarial loop re-tests through
    verified_offline: (
        bool | None
    )  # (c): bool now; (a): null → verified by the MC-02 re-scan


class AdversarialLoopView(BaseModel):
    """The closed offense↔defense loop (MC-02) — exploit → patch → re-scan → adapt.

    DERIVED by actually running the loop (`keystone.agents.adversarial.close_loop`): the
    Red-Team's exploit, the Defense Agent's applied remediation, the RE-SCAN of the PATCHED
    target, and the Red-Team's ADAPTATION to the post-patch observation. `kind` states which
    remediation's loop ran and is honest about the difference: "ai_rescan" = a REAL re-scan of
    the guarded target ((a); `pre_patch`/`post_patch` fails measured, `mitigated` computed);
    "financial_reverify" = the OFFLINE detection re-verify ((c); no AI target, `post_patch` null,
    `source` "offline"). `source` tags the re-scan (garak_live / recorded_profile), never a
    fallback reported as a live scan. `mitigated` is MEASURED, not assumed.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    remediation_control: str
    side: str  # "ai" | "financial"
    kind: str  # "ai_rescan" | "financial_reverify"
    probe: str | None  # the exploited probe re-tested (a); null for (c)
    pre_patch_fails: int
    pre_patch_total: int
    post_patch_fails: int | None  # measured on the patched target (a); null for (c)
    post_patch_total: int | None
    mitigated: (
        bool  # the patch changed the outcome (exploit no longer lands / gap covered)
    )
    source: str  # "garak_live" | "recorded_profile" (a) | "offline" (c)
    adaptation: str  # how the Red-Team responds to the post-patch observation
    adapted_exploited_family: (
        str | None
    )  # what it exploits post-patch (null = defense held)


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
    # The Triage Agent's recorded routing decision (MB-01) — the supervisor over the
    # offense worker's finding; the route depends on the signal interplay (not a rule).
    triage: TriageView
    # The Defense Agent's recorded remediation choice (MC-01) — the defender that chooses
    # (a) block the AI side vs (c) tighten the money side. OPTIONAL + defaulted None so a run
    # recorded before the Defense Agent existed still loads (no schema bump — mirrors how
    # OPT-A-01's `reasoner` / OPT-A-02's `source` were added).
    defense: DefenseView | None = None
    # The closed adversarial loop (MC-02) — offense→defense→re-scan→adapt. OPTIONAL + defaulted
    # None so a run recorded before the loop existed still loads (no schema bump).
    adversarial_loop: AdversarialLoopView | None = None
