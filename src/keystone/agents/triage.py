"""The Triage Agent (MB-01) — Keystone's second genuine agent → multi-agent.

A **supervisory triage policy** (MB-00 §3, Option B): it observes a security
finding's already-computed signals — its ``failure_rate`` (how hard the attack got
through), its ``seam_result`` (CLEAN / BOUNDARY / OPEN — how the seam classifies),
and its mapped ``severity`` — and routes the finding to one of three actions:
**remediate / accept / escalate**. The route is a function of how the signals
*combine*, NOT a single threshold: the SAME failure_rate routes DIFFERENTLY
depending on the seam context. That is the MB-00 §2 honesty test
(``tests/test_triage_agent.py``) and it is what makes this an agent and not an
``if failure_rate > X``.

**Honest framing (MB-00 §3).** This is an *adaptive triage policy*, NOT an LLM
agent. It clears MB-00 §2's bar — the route demonstrably depends on the interplay of
≥2 signals, with a genuine ≥2-option action space — but it reasons through an
explicit, transparent policy (:func:`route_for`), not model inference. We do not
claim "LLM agent" while shipping a policy; Option A (LLM-reasoned triage) is a later
upgrade.

**Scope honesty (MB-00 §1/§6).** "remediate" is a ROUTE — *this finding warrants
remediation* — NOT a Defense Agent choosing among fixes. The Triage Agent decides
*whether / what priority*, not *which fix*; fix-selection (the adversarial loop) is
gated Movement C and is NOT claimed here.

**The decision space is real.** Three routes (:class:`Route`), each genuinely
reachable on realistic findings (``tests/test_triage_agent.py`` constructs a finding
for each), so "route" is genuinely meaningful — no 2-of-3-dead agency-theater.

**Topology: supervisor–worker (MB-00 §1).** With MA-01, this is the second genuine
agent and the one that makes Keystone formally **multi-agent**: the Triage Agent
(supervisor) reasons over the finding the Red-Team Agent (offensive worker) produced
— the ``failure_rate`` it reads IS the worker's strongest landed exploit.

**The memo-blind boundary (MB-00 §4, sacred).** This agent reads ONLY the
already-computed signals, as plain values. It NEVER reaches into the L1 detector or
the attack channel: it imports nothing on the detection path — not the FATF engine,
not the seam framework's ``project_financial`` / ``detect``, not the input-rail
detector, not the Garak scanner. To keep that boundary structural (an AST import-scan
asserts it, ``tests/test_triage_boundary.py``), the agent carries its OWN value
representation of the two typed signals (:class:`SeamClassification`,
:class:`FindingSeverity`) instead of importing the detection modules that define them;
a parity test pins those values to the originals so they cannot drift. The
independence invariants hold with BOTH agents present.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class SeamClassification(StrEnum):
    """The seam result the agent OBSERVES — an already-computed signal, read as a value.

    Mirrors ``keystone.assurance.framework.SeamResult`` BY VALUE (a parity test pins
    them), but is defined here so the agent imports nothing from the detection
    framework (the memo-blind boundary, MB-00 §4 — that module also holds
    ``project_financial`` / ``CrimeSide.detect``).

    CLEAN — the seam binds (attack and crime are the same event): a real path.
    BOUNDARY — the seam provably does NOT bind (characterized non-binding): contained.
    OPEN — outcome reported as-found, not yet certain: unresolved.
    """

    CLEAN = "clean"
    BOUNDARY = "boundary"
    OPEN = "open"


class FindingSeverity(StrEnum):
    """The mapped severity the agent OBSERVES — an already-computed signal, as a value.

    Mirrors ``keystone.core.fatf.models.Severity`` BY VALUE (a parity test pins them),
    defined here so the agent imports nothing from the deterministic core / detection
    path (MB-00 §4).
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Route(StrEnum):
    """The 3-option action space — each genuinely reachable (no dead route, MB-00 §3).

    REMEDIATE — real & resolvable: this finding warrants a patch (a ROUTE, not a
        choice among fixes — fix-selection is gated Movement C, MB-00 §6).
    ACCEPT — contained / low-impact: nothing actionable here.
    ESCALATE — dangerous-in-context: a human must see this finding.
    """

    REMEDIATE = "remediate"
    ACCEPT = "accept"
    ESCALATE = "escalate"


# Below this attack failure_rate, nothing is actionable — the noise floor. A finding
# that barely got through is contained on rate grounds alone (unless it is severe).
ACTION_FLOOR = 0.10

# Honest, one-line description of the mechanism, surfaced in the trace/UI/paper.
MECHANISM = "adaptive triage policy (routes over signal interplay; not an LLM)"


class TriageSignals(BaseModel):
    """The OBSERVED STATE: a finding's already-computed signals (read-only).

    The agent READS these — it never recomputes them and never reaches into the
    detector or the attack channel that produced them (MB-00 §4). ``failure_rate``
    is the attack's exploit strength (the offense worker's reading), ``seam_result``
    how the seam classifies, ``severity`` the mapped finding severity.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    failure_rate: float
    seam_result: SeamClassification
    severity: FindingSeverity


def route_for(signals: TriageSignals) -> Route:
    """THE reasoning step: route the finding over the COMBINATION of its signals.

    Transparent triage policy (MB-00 §3, Option B). The route is a function of how the
    three signals *combine*, not a single threshold — the property the MB-00 §2
    interplay test exercises (same ``failure_rate``, different ``seam_result`` →
    different route):

    1. **Escalate (severe-in-itself)** — a HIGH-severity finding warrants human eyes
       regardless of rate: an unresolved/severe finding a human must see.
    2. **Accept (below the floor)** — a finding that barely got through is contained on
       rate grounds: nothing actionable.
    3. **Above the floor, not high-severity — the SEAM CONTEXT decides what the rate
       means** (this is the interplay):
       - **Escalate** when OPEN: an unresolved seam result with a non-trivial rate
         needs a human to resolve.
       - **Accept** when BOUNDARY: the seam provably does not bind — contained,
         characterized non-binding, even at the same rate.
       - **Remediate** when CLEAN: the seam binds — a real, resolvable vulnerability
         the system should patch.

    The same ``failure_rate`` therefore routes to remediate / accept / escalate
    depending on whether the seam is CLEAN / BOUNDARY / OPEN — not a single threshold.
    """
    if signals.severity is FindingSeverity.HIGH:
        return Route.ESCALATE
    if signals.failure_rate < ACTION_FLOOR:
        return Route.ACCEPT
    # Above the floor, not high-severity: the seam context decides what the rate means.
    if signals.seam_result is SeamClassification.OPEN:
        return Route.ESCALATE
    if signals.seam_result is SeamClassification.BOUNDARY:
        return Route.ACCEPT
    return Route.REMEDIATE  # CLEAN


def _rationale(signals: TriageSignals, route: Route) -> str:
    """Plain-language WHY for this route — grounded in the signals that drove it.

    States which signals were decisive, so the audit trail shows the route was driven
    by the observed combination, not a single fixed threshold.
    """
    rate = f"{signals.failure_rate:.0%}"
    seam = signals.seam_result.value
    sev = signals.severity.value
    if signals.severity is FindingSeverity.HIGH:
        return (
            f"HIGH-severity finding ({rate} exploit on a {seam} seam) — a human must "
            f"see a severe finding regardless of rate; escalating."
        )
    if signals.failure_rate < ACTION_FLOOR:
        return (
            f"Exploit rate {rate} is below the action floor of {ACTION_FLOOR:.0%} "
            f"(severity {sev}) — nothing actionable; accepting."
        )
    if signals.seam_result is SeamClassification.OPEN:
        return (
            f"Open (unresolved) seam result with a non-trivial {rate} exploit rate "
            f"(severity {sev}) — needs a human to resolve; escalating."
        )
    if signals.seam_result is SeamClassification.BOUNDARY:
        return (
            f"Boundary seam result — the seam provably does not bind, so a {rate} "
            f"exploit rate is contained (severity {sev}); accepting."
        )
    return (
        f"Clean seam result with a {rate} exploit rate above the {ACTION_FLOOR:.0%} "
        f"floor (severity {sev}) — a real, resolvable vulnerability; remediating."
    )


class TriageDecision(BaseModel):
    """The agent's decision: the route + the signals it saw + why (the audit trail).

    This is the artifact record/replay (MB-00 §4) preserves: a faithful capture of a
    genuine triage decision, replayed deterministically (the policy is a pure function
    of the observed signals, so the same finding always routes the same way).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    signals: TriageSignals
    route: Route
    rationale: str


def triage(signals: TriageSignals) -> TriageDecision:
    """Run the agent: observe (the signals) → reason (the policy) → route.

    The route at the heart of the decision is :func:`route_for` applied to the
    observed combination — so the decision is genuinely a function of what the agent
    observed, the property the MB-00 §2 interplay test exercises.
    """
    route = route_for(signals)
    return TriageDecision(
        signals=signals,
        route=route,
        rationale=_rationale(signals, route),
    )
