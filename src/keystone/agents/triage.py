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

**Honest framing (MB-00 §3 / OPT-A-00).** In the default (offline) path this is an
*adaptive triage policy*, NOT an LLM agent: it clears MB-00 §2's bar — the route
demonstrably depends on the interplay of ≥2 signals, with a genuine ≥2-option action
space — but it reasons through an explicit, transparent policy (:func:`route_for`),
not model inference. OPT-A-01 adds an **opt-in live mode** (:func:`live_triage`): a
local LLM (qwen2.5:3b via Ollama) reasons the route over the SAME signals, constrained
to the same 3-option space, with the policy as a proven fallback. The recorded decision
always tags WHICH reasoner ran (``reasoner``: ``policy`` / ``policy_fallback`` /
``llm:<model>``) — we never claim "LLM" while shipping the policy (OPT-A-00 §3).

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

import re
from collections.abc import Callable
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from keystone.llm.inference import Backend, InferenceError, complete, get_backend


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

# Reasoner tags — the honesty guarantee (OPT-A-00 §3): the recorded decision states
# WHICH reasoner produced the route. Never report a fallback as an LLM decision.
#   POLICY          — the deterministic policy ran (the offline default).
#   POLICY_FALLBACK — live mode asked, but the LLM was unavailable / timed out /
#                     returned unparseable-or-out-of-space output → the policy ran.
#   llm:<model>     — a live LLM genuinely reasoned the route (see llm_reasoner_tag).
POLICY_REASONER = "policy"
POLICY_FALLBACK_REASONER = "policy_fallback"


def llm_reasoner_tag(model: str) -> str:
    """The reasoner tag for a route produced by a live LLM (e.g. ``llm:qwen2.5:3b``)."""
    return f"llm:{model}"


def mechanism_for(reasoner: str) -> str:
    """The honest one-line mechanism label matching the reasoner that actually ran.

    In live LLM mode it says "LLM-reasoned triage"; on fallback it says the policy ran
    because the LLM was unavailable; offline it is the transparent policy label. The
    label must always match what ran (OPT-A-00 §2) — so it is derived from the tag.
    """
    if reasoner.startswith("llm:"):
        model = reasoner[len("llm:") :]
        return (
            f"LLM-reasoned triage ({model}); bounded selection over the 3 routes, "
            f"grounded in the signals (not the attack channel)"
        )
    if reasoner == POLICY_FALLBACK_REASONER:
        return f"{MECHANISM} - LLM unavailable in live mode; fell back to the policy"
    return MECHANISM


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
    # WHICH reasoner produced this route (OPT-A-00 §3). Defaults to the policy tag so
    # the deterministic path (and any decision recorded before live mode existed) is
    # truthfully labelled a policy run.
    reasoner: str = POLICY_REASONER


def triage(signals: TriageSignals) -> TriageDecision:
    """Run the agent: observe (the signals) → reason (the policy) → route.

    The route at the heart of the decision is :func:`route_for` applied to the
    observed combination — so the decision is genuinely a function of what the agent
    observed, the property the MB-00 §2 interplay test exercises. This is the offline
    default and the live fallback; the reasoner is the transparent policy.
    """
    route = route_for(signals)
    return TriageDecision(
        signals=signals,
        route=route,
        rationale=_rationale(signals, route),
        reasoner=POLICY_REASONER,
    )


# --------------------------------------------------------------------------- #
# Live mode (OPT-A-01): genuine LLM reasoning, opt-in, policy as the fallback.  #
# The LLM reasons over the SAME three signals the policy reads — NEVER the raw  #
# memo / attack channel (the memo-blind boundary, OPT-A-00 §4, stays sacred).   #
# --------------------------------------------------------------------------- #

# Bounded selection, not open reasoning (OPT-A-00 §7.3): a 3B model picks reliably
# from a fixed set but may not plan freely. `/no_think` keeps the reply terse.
TRIAGE_SYSTEM = (
    "/no_think\n"
    "You are a security-triage router. You are given three already-computed signals "
    "about a security finding and a fixed set of allowed routes. Choose EXACTLY ONE "
    "route from the allowed set — never invent a route. Reply with ONLY one line:\n"
    "ROUTE: <one of the allowed routes> | WHY: <one short sentence>"
)


class LlmRouteChoice(BaseModel):
    """A parsed, VALIDATED LLM routing choice: a route in the space + its rationale.

    Only ever constructed from an LLM answer that named exactly one allowed route
    (:func:`parse_llm_choice`); an out-of-space or unparseable answer yields ``None``
    and the caller falls back to the policy — the route is never coerced or invented.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    route: Route
    rationale: str


# A live reasoner: given the signals and the allowed routes, return a validated choice,
# or None when it cannot (unavailable / timeout / unparseable) so the caller falls back.
LlmReasoner = Callable[[TriageSignals, tuple[Route, ...]], LlmRouteChoice | None]


def build_live_prompt(signals: TriageSignals, routes: tuple[Route, ...]) -> str:
    """Render the signals + allowed routes as the LLM prompt — SIGNALS ONLY.

    The prompt carries the three abstract signals (a rate, a seam class, a severity)
    and the three route meanings. It NEVER carries the raw memo, the attack channel, or
    any detector internals (OPT-A-00 §4, sacred) — putting the attack text here "to
    reason better" is the exact forbidden landmine.
    """
    return (
        f"failure_rate: {signals.failure_rate:.2f}  "
        "(0.0 = the attack got nothing through, 1.0 = full exploit)\n"
        f"seam_result: {signals.seam_result.value}  "
        "(clean = the seam binds, a real path; boundary = provably contained; "
        "open = unresolved)\n"
        f"severity: {signals.severity.value}\n"
        f"allowed routes: {', '.join(r.value for r in routes)}\n"
        "Route meanings — "
        f"{Route.REMEDIATE.value}: a real, resolvable vulnerability to patch; "
        f"{Route.ACCEPT.value}: contained / not actionable; "
        f"{Route.ESCALATE.value}: a human must review this finding.\n"
        "Choose exactly one allowed route for this finding."
    )


def parse_llm_choice(text: str, routes: tuple[Route, ...]) -> LlmRouteChoice | None:
    """Parse+validate an LLM answer into a route strictly within ``routes``, or None.

    Constrained-output discipline (OPT-A-00 §5): an answer that names exactly one
    allowed route is accepted; garbage, silence, an out-of-space word, or an ambiguous
    multi-route answer returns None so the caller falls back — never a coerced route.
    """
    if not text or not text.strip():
        return None
    lowered = text.lower()
    allowed = {r.value: r for r in routes}

    # Prefer an explicit "ROUTE: <x>" declaration; it must name an ALLOWED route.
    declared = re.search(r"route\s*[:=]\s*([a-z]+)", lowered)
    if declared is not None:
        route = allowed.get(declared.group(1))
        if route is None:
            return None  # declared something outside the allowed set → invalid
    else:
        # No declaration: accept only if EXACTLY ONE allowed route word is present.
        present = [
            r for v, r in allowed.items() if re.search(rf"\b{re.escape(v)}\b", lowered)
        ]
        if len(present) != 1:
            return None
        route = present[0]

    why = re.search(r"why\s*[:=]\s*(.+)", text, flags=re.IGNORECASE)
    rationale = why.group(1).strip() if why is not None else text.strip()
    return LlmRouteChoice(route=route, rationale=f"[LLM] {rationale}")


def ollama_reasoner(*, backend: Backend | None = None) -> LlmReasoner:
    """Build a live reasoner backed by the inference seam (Ollama qwen2.5:3b default).

    Reuses the one allowed LLM path (:func:`keystone.llm.inference.complete`, ADR-0008);
    no new client. Any inference failure (unreachable / timeout / HTTP error) is turned
    into ``None`` here so the caller falls back to the policy — live is never a regression.
    """

    def _reason(
        signals: TriageSignals, routes: tuple[Route, ...]
    ) -> LlmRouteChoice | None:
        try:
            text = complete(
                build_live_prompt(signals, routes),
                system=TRIAGE_SYSTEM,
                backend=backend,
            )
        except InferenceError:
            return None  # unavailable / timeout / HTTP error → fall back to the policy
        return parse_llm_choice(text, routes)

    return _reason


def triage_live(
    signals: TriageSignals, *, reasoner: LlmReasoner, model_tag: str
) -> TriageDecision:
    """Run the agent in LIVE mode: the LLM reasons; on any failure, fall back — TAGGED.

    The route is ALWAYS produced (OPT-A-00 §3): if the reasoner returns a validated
    choice, the decision is tagged ``model_tag`` (``llm:<model>``) with the LLM's
    rationale; if it returns None (unavailable / unparseable / out-of-space), the proven
    policy produces the route and the decision is tagged ``policy_fallback``. The tag
    always states what actually ran — a fallback is never reported as an LLM decision.
    """
    choice = reasoner(signals, tuple(Route))
    if choice is None:
        route = route_for(signals)
        return TriageDecision(
            signals=signals,
            route=route,
            rationale=_rationale(signals, route),
            reasoner=POLICY_FALLBACK_REASONER,
        )
    return TriageDecision(
        signals=signals,
        route=choice.route,
        rationale=choice.rationale,
        reasoner=model_tag,
    )


def _backend_model(backend: Backend) -> str:
    """The model name of a concrete backend (for the ``llm:<model>`` tag), typed-safe."""
    model = getattr(backend, "model", None)
    return model if isinstance(model, str) else "unknown"


def live_triage(
    signals: TriageSignals, *, backend: Backend | None = None
) -> TriageDecision:
    """Convenience live entry: reason with the env-configured backend, policy fallback.

    Builds the Ollama-backed reasoner and the ``llm:<model>`` tag from the active
    backend, then runs :func:`triage_live`. The offline console arc uses :func:`triage`;
    this is reached only when the caller explicitly opts into live mode.
    """
    active = backend if backend is not None else get_backend()
    return triage_live(
        signals,
        reasoner=ollama_reasoner(backend=active),
        model_tag=llm_reasoner_tag(_backend_model(active)),
    )
