"""The live Triage Agent (OPT-A-01) — the honesty tests (OPT-A-00 §5).

The Triage Agent gains an opt-in LIVE mode: a local LLM reasons the route over the
same signals, constrained to the same 3-option space, with the proven policy as the
fallback. These tests pin the three honesty guarantees the design fixed BEFORE code:

1. **Reasoner-honesty** — the recorded decision tags WHICH reasoner ran (``llm:<model>``
   vs ``policy_fallback``); a fallback is NEVER reported as an LLM decision.
2. **Constrained output** — a garbage / out-of-space / ambiguous LLM answer falls back
   to the policy; the route is NEVER coerced or invented outside {remediate,accept,escalate}.
3. **Boundary (sacred)** — the LLM prompt carries the three signals ONLY, never the raw
   memo / attack channel / detector internals (OPT-A-00 §4).

All fast-gate tests inject a fake backend / reasoner so the gate never touches Ollama or
a network. The single real-LLM check is ``slow`` and skips cleanly if Ollama is down —
the offline default must work with no live model.
"""

from __future__ import annotations

import pytest

# The eval's scenario tables (scripts/ is on pythonpath + mypy_path), used to prove the
# prompt's few-shot examples are held out from everything the evaluation routes.
from triage_llm_eval import HELDOUT_SCENARIOS, SCENARIOS

from keystone.agents.red_team import PROBE_CATALOG
from keystone.agents.triage import (
    POLICY_FALLBACK_REASONER,
    POLICY_REASONER,
    TRIAGE_SYSTEM,
    FindingSeverity,
    LlmRouteChoice,
    Route,
    SeamClassification,
    TriageSignals,
    build_live_prompt,
    live_triage,
    llm_reasoner_tag,
    mechanism_for,
    ollama_reasoner,
    parse_llm_choice,
    route_for,
    triage_live,
)
from keystone.assurance.framework import SeamResult
from keystone.core.fatf.models import Severity
from keystone.demo.triage import build_triage_view
from keystone.llm.inference import BackendUnreachableError, InferenceError

ROUTES = tuple(Route)


def _signals(
    failure_rate: float = 0.5,
    seam_result: SeamClassification = SeamClassification.CLEAN,
    severity: FindingSeverity = FindingSeverity.MEDIUM,
) -> TriageSignals:
    return TriageSignals(
        failure_rate=failure_rate, seam_result=seam_result, severity=severity
    )


# --- fakes: injected so the fast gate never touches Ollama --------------------


class _FakeBackend:
    """A backend that returns a canned completion (never touches the network)."""

    model = "fake-model"

    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.last_prompt: str | None = None
        self.last_system: str | None = None

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        self.last_prompt = prompt
        self.last_system = system
        return self.reply


class _UnreachableBackend:
    """A backend whose every call fails as if Ollama were down."""

    model = "down-model"

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        raise BackendUnreachableError("Ollama backend unreachable (is it running?)")


# --- 1. reasoner-honesty (OPT-A-00 §3/§5) -------------------------------------


def test_llm_choice_records_the_llm_reasoner_tag() -> None:
    # A working reasoner → the decision is tagged the LLM model, with the LLM rationale.
    decision = triage_live(
        _signals(),
        reasoner=lambda s, routes: LlmRouteChoice(
            route=Route.ESCALATE, rationale="the model's reason"
        ),
        model_tag="llm:qwen2.5:3b",
    )
    assert decision.reasoner == "llm:qwen2.5:3b"
    assert decision.route is Route.ESCALATE
    assert decision.rationale == "the model's reason"


def test_unavailable_llm_records_policy_fallback_not_llm() -> None:
    # THE guarantee: when the reasoner cannot decide (returns None), the policy produces
    # the route and the decision is tagged policy_fallback — never claimed as an LLM call.
    signals = _signals(0.5, SeamClassification.CLEAN, FindingSeverity.MEDIUM)
    decision = triage_live(
        signals, reasoner=lambda s, routes: None, model_tag="llm:qwen2.5:3b"
    )
    assert decision.reasoner == POLICY_FALLBACK_REASONER
    # The route is exactly what the proven policy would produce — never degraded.
    assert decision.route is route_for(signals)


def test_reasoner_tag_matches_what_actually_ran_via_the_backend() -> None:
    # End-to-end through the Ollama seam: a reachable fake backend → llm tag; an
    # unreachable one → policy_fallback. The tag tracks what actually ran.
    reachable = _FakeBackend("ROUTE: accept | WHY: contained")
    llm_decision = triage_live(
        _signals(),
        reasoner=ollama_reasoner(backend=reachable),
        model_tag=llm_reasoner_tag(reachable.model),
    )
    assert llm_decision.reasoner == "llm:fake-model"
    assert llm_decision.route is Route.ACCEPT

    down = _UnreachableBackend()
    fb_decision = triage_live(
        _signals(),
        reasoner=ollama_reasoner(backend=down),
        model_tag=llm_reasoner_tag(down.model),
    )
    assert fb_decision.reasoner == POLICY_FALLBACK_REASONER


def test_mechanism_label_always_matches_the_reasoner() -> None:
    # The human mechanism label must match the machine tag (OPT-A-00 §2) — never say
    # "LLM-reasoned" for a policy run, or vice versa.
    assert "not an LLM" in mechanism_for(POLICY_REASONER)
    assert "fell back" in mechanism_for(POLICY_FALLBACK_REASONER)
    assert mechanism_for("llm:qwen2.5:3b").startswith(
        "LLM-reasoned triage (qwen2.5:3b)"
    )


# --- 2. constrained output (OPT-A-00 §5) --------------------------------------


def test_valid_llm_answer_parses_to_the_declared_route() -> None:
    choice = parse_llm_choice("ROUTE: escalate | WHY: unresolved seam", ROUTES)
    assert choice is not None
    assert choice.route is Route.ESCALATE
    assert "unresolved seam" in choice.rationale


def test_a_single_bare_route_word_is_accepted() -> None:
    choice = parse_llm_choice("I think we should remediate this finding.", ROUTES)
    assert choice is not None and choice.route is Route.REMEDIATE


@pytest.mark.parametrize(
    "garbage",
    [
        "",
        "   ",
        "purple monkey dishwasher",  # no route word
        "ROUTE: delete",  # out-of-space word declared
        "ROUTE: quarantine | WHY: made up",  # invented route
        "maybe accept, or perhaps escalate",  # ambiguous (two routes)
    ],
)
def test_unparseable_or_out_of_space_answers_return_none(garbage: str) -> None:
    # Never coerce: anything not naming exactly one ALLOWED route yields None → fallback.
    assert parse_llm_choice(garbage, ROUTES) is None


def test_garbage_llm_output_falls_back_cleanly_never_coerced() -> None:
    # A backend returning garbage → the live path falls back to the policy route and
    # tags it policy_fallback; it NEVER invents or coerces a route.
    signals = _signals(0.5, SeamClassification.OPEN, FindingSeverity.MEDIUM)
    decision = triage_live(
        signals,
        reasoner=ollama_reasoner(backend=_FakeBackend("lorem ipsum dolor")),
        model_tag="llm:fake-model",
    )
    assert decision.reasoner == POLICY_FALLBACK_REASONER
    assert decision.route is route_for(signals)
    assert decision.route in set(Route)


def test_inference_error_from_the_backend_falls_back() -> None:
    # An HTTP/timeout failure (InferenceError) inside the reasoner → None → fallback,
    # not a crashed arc. (Unreachable is the BackendUnreachableError subclass case.)
    class _HttpErrorBackend:
        model = "err-model"

        def complete(self, prompt: str, *, system: str | None = None) -> str:
            raise InferenceError("Ollama backend returned HTTP 500")

    reasoner = ollama_reasoner(backend=_HttpErrorBackend())
    assert reasoner(_signals(), ROUTES) is None


# --- 3. interplay preserved (the §2 MB bar, now for the live path) ------------


def test_live_path_can_route_over_signal_interplay() -> None:
    # A genuine reasoner routes DIFFERENTLY by context. Model a signal-sensitive reasoner
    # (mirrors what a good LLM should do) and prove the live path carries the interplay:
    # same rate/severity, different seam → different route.
    def _by_seam(signals: TriageSignals, routes: tuple[Route, ...]) -> LlmRouteChoice:
        mapping = {
            SeamClassification.CLEAN: Route.REMEDIATE,
            SeamClassification.BOUNDARY: Route.ACCEPT,
            SeamClassification.OPEN: Route.ESCALATE,
        }
        return LlmRouteChoice(route=mapping[signals.seam_result], rationale="by seam")

    rate = 0.5
    routes = {
        seam: triage_live(
            _signals(rate, seam), reasoner=_by_seam, model_tag="llm:fake"
        ).route
        for seam in SeamClassification
    }
    assert len(set(routes.values())) == 3  # three seams → three routes, same rate


def test_fallback_still_honors_interplay() -> None:
    # Even when the LLM is unavailable, the fallback is the interplay-honoring policy:
    # same rate/severity, different seam → different route (the MB-00 §2 property holds).
    rate = 0.5
    routes = {
        seam: triage_live(
            _signals(rate, seam), reasoner=lambda s, r: None, model_tag="llm:fake"
        ).route
        for seam in SeamClassification
    }
    assert len(set(routes.values())) == 3


# --- 4. the boundary (OPT-A-00 §4, sacred) ------------------------------------


def test_live_prompt_carries_signals_only_never_the_attack_channel() -> None:
    # The prompt contains the three signals and route meanings — and NONE of the attack
    # vocabulary (probe names). The attack text must never ride into the LLM prompt.
    prompt = build_live_prompt(
        _signals(0.83, SeamClassification.CLEAN, FindingSeverity.HIGH), ROUTES
    )
    assert "0.83" in prompt and "clean" in prompt and "HIGH" in prompt
    every_probe = {p for fam in PROBE_CATALOG.values() for p in fam}
    assert not any(probe in prompt for probe in every_probe)
    # No detector/memo tokens leak in either.
    for forbidden in ("memo", "prompt injection", "garak", "detect"):
        assert forbidden.lower() not in prompt.lower()


def test_system_prompt_constrains_to_bounded_selection() -> None:
    # The system prompt tells the model to pick EXACTLY ONE allowed route — bounded
    # selection, not open planning (OPT-A-00 §7.3).
    assert "EXACTLY ONE" in TRIAGE_SYSTEM
    assert "never invent" in TRIAGE_SYSTEM.lower()


# The few-shot worked examples baked into TRIAGE_SYSTEM (OPT-A-01b lever 3). Held here as
# data so a mechanical test can prove they still match the policy ground truth: a prompt
# that teaches the model an example the policy would NOT produce is a silent correctness
# bug. If TRIAGE_SYSTEM's examples change, update this table — the test re-checks route_for.
_FEWSHOT_EXAMPLES: tuple[
    tuple[float, SeamClassification, FindingSeverity, Route], ...
] = (
    (0.65, SeamClassification.CLEAN, FindingSeverity.MEDIUM, Route.REMEDIATE),
    (0.65, SeamClassification.BOUNDARY, FindingSeverity.MEDIUM, Route.ACCEPT),
    (0.65, SeamClassification.OPEN, FindingSeverity.MEDIUM, Route.ESCALATE),
    (0.05, SeamClassification.CLEAN, FindingSeverity.LOW, Route.ACCEPT),
    (0.90, SeamClassification.BOUNDARY, FindingSeverity.HIGH, Route.ESCALATE),
)


def test_fewshot_examples_match_the_policy_ground_truth() -> None:
    # Every worked example the prompt teaches must be a route the policy would actually
    # produce — the prompt cannot teach the model a decision that contradicts route_for.
    for rate, seam, sev, expected in _FEWSHOT_EXAMPLES:
        assert route_for(_signals(rate, seam, sev)) is expected
        # …and each example's declared route is really present in the system prompt.
        assert f"ROUTE: {expected.value}" in TRIAGE_SYSTEM


def test_fewshot_example_rates_are_held_out_from_the_eval_scenarios() -> None:
    # The examples must use different (rate, seam, severity) tuples than anything the
    # eval routes, so the evaluation tests generalization, not memorization (OPT-A-01b).
    example_tuples = {(r, s, v) for r, s, v, _ in _FEWSHOT_EXAMPLES}
    eval_tuples = {
        (sig.failure_rate, sig.seam_result, sig.severity)
        for _, sig in (*SCENARIOS, *HELDOUT_SCENARIOS)
    }
    assert example_tuples.isdisjoint(eval_tuples)


# --- 5. the offline default is UNCHANGED (front door works with no Ollama) ----


def test_build_triage_view_offline_is_the_policy_and_needs_no_llm() -> None:
    # The default (live=False) path is the transparent policy — reasoner "policy", the
    # policy route, the policy mechanism label. No backend is touched.
    view = build_triage_view(
        failure_rate=0.83,
        seam_result=SeamResult.CLEAN,
        severity=Severity.MEDIUM,
    )
    assert view.reasoner == POLICY_REASONER
    assert view.route == Route.REMEDIATE.value
    assert "not an LLM" in view.mechanism


def test_build_triage_view_live_with_a_fake_backend_tags_llm() -> None:
    # live=True with an injected reachable backend → an llm-tagged view (no real Ollama).
    view = build_triage_view(
        failure_rate=0.5,
        seam_result=SeamResult.CLEAN,
        severity=Severity.MEDIUM,
        live=True,
        backend=_FakeBackend("ROUTE: remediate | WHY: clean seam, real vuln"),
    )
    assert view.reasoner == "llm:fake-model"
    assert view.route == Route.REMEDIATE.value
    assert view.mechanism.startswith("LLM-reasoned triage")


def test_build_triage_view_live_falls_back_when_backend_down() -> None:
    view = build_triage_view(
        failure_rate=0.5,
        seam_result=SeamResult.OPEN,
        severity=Severity.MEDIUM,
        live=True,
        backend=_UnreachableBackend(),
    )
    assert view.reasoner == POLICY_FALLBACK_REASONER
    assert "fell back" in view.mechanism


# --- 6. the ONE real-LLM smoke check (slow; skips if Ollama is down) ----------


@pytest.mark.slow
def test_real_qwen_produces_a_route_in_the_space_or_falls_back() -> None:
    # A genuine call to qwen2.5:3b via Ollama. We do NOT assert WHICH route (that is the
    # open evaluation, not a gate) — only that live mode is honest: the result is in the
    # 3-route space and tagged either llm:<model> or policy_fallback, never anything else.
    decision = live_triage(
        _signals(0.83, SeamClassification.CLEAN, FindingSeverity.HIGH)
    )
    assert decision.route in set(Route)
    assert (
        decision.reasoner == POLICY_FALLBACK_REASONER
        or decision.reasoner.startswith("llm:")
    )
