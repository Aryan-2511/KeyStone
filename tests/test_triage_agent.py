"""The Triage Agent (MB-01) — the §2 honesty test: an agent, not a threshold.

THE load-bearing test (MB-00 §2): hold ``failure_rate`` FIXED and vary the seam
context → the route must CHANGE. If the route never changed when the non-target
signals varied, this would be a single-signal threshold in costume — the build would
fail here. The companion tests prove all three routes are genuinely reachable and that
the policy is a deterministic function of the observed combination (so it replays).

Fast and deterministic: the policy is a pure function of typed signals (no Garak, no
network, no detector), so these tests exercise the reasoning step directly.
"""

from __future__ import annotations

import pytest

from keystone.agents.triage import (
    ACTION_FLOOR,
    FindingSeverity,
    Route,
    SeamClassification,
    TriageSignals,
    route_for,
    triage,
)
from keystone.assurance.framework import SeamResult
from keystone.core.fatf.models import Severity


def _signals(
    failure_rate: float,
    seam_result: SeamClassification,
    severity: FindingSeverity = FindingSeverity.MEDIUM,
) -> TriageSignals:
    return TriageSignals(
        failure_rate=failure_rate, seam_result=seam_result, severity=severity
    )


# --- THE honesty test (MB-00 §2): interplay, not a single threshold -----------


def test_same_rate_routes_differently_by_seam_context() -> None:
    # THE interplay test. Hold failure_rate FIXED (a moderate, above-floor rate) and
    # hold severity FIXED (MEDIUM) — vary ONLY the seam result. The route must change.
    # This is the literal "not a single threshold" proof: the same rate means three
    # different things depending on the seam context.
    rate = 0.50
    clean = route_for(_signals(rate, SeamClassification.CLEAN))
    boundary = route_for(_signals(rate, SeamClassification.BOUNDARY))
    open_ = route_for(_signals(rate, SeamClassification.OPEN))

    # Same failure_rate, same severity → THREE different routes, by seam context alone.
    assert clean == Route.REMEDIATE
    assert boundary == Route.ACCEPT
    assert open_ == Route.ESCALATE
    assert len({clean, boundary, open_}) == 3

    # If the route were a pure function of failure_rate, these would all be equal.
    # They are not — the route depends on the COMBINATION (the agency bar, MB-00 §2).


def test_route_is_not_a_pure_function_of_any_single_signal() -> None:
    # No single signal determines the route — each, held at one value, yields multiple
    # routes depending on the others (the formal "interplay, not threshold" statement).

    # failure_rate fixed at 0.50 → all three routes appear (varying seam).
    fixed_rate = {
        route_for(_signals(0.50, s))
        for s in (
            SeamClassification.CLEAN,
            SeamClassification.BOUNDARY,
            SeamClassification.OPEN,
        )
    }
    assert len(fixed_rate) == 3

    # seam fixed at CLEAN → route still varies (accept below floor, remediate above,
    # escalate when severe): not a function of the seam alone.
    fixed_seam = {
        route_for(_signals(0.01, SeamClassification.CLEAN)),  # below floor → accept
        route_for(_signals(0.50, SeamClassification.CLEAN)),  # above floor → remediate
        route_for(  # high severity → escalate
            _signals(0.50, SeamClassification.CLEAN, FindingSeverity.HIGH)
        ),
    }
    assert fixed_seam == {Route.ACCEPT, Route.REMEDIATE, Route.ESCALATE}

    # severity fixed at MEDIUM → route still varies (the three-by-seam case above is
    # all MEDIUM): not a function of severity alone.
    assert len(fixed_rate) == 3  # (the fixed_rate set above was all MEDIUM severity)


# --- all three routes are genuinely reachable (no 2-of-3-dead) -----------------


def test_all_three_routes_are_reachable_on_realistic_findings() -> None:
    # A realistic finding for EACH route — the decision space is genuine, not theater.
    remediate = triage(_signals(0.83, SeamClassification.CLEAN, FindingSeverity.MEDIUM))
    accept = triage(_signals(0.0, SeamClassification.BOUNDARY, FindingSeverity.LOW))
    escalate = triage(_signals(0.83, SeamClassification.CLEAN, FindingSeverity.HIGH))

    assert remediate.route == Route.REMEDIATE
    assert accept.route == Route.ACCEPT
    assert escalate.route == Route.ESCALATE
    # Every route is in the genuine 3-option space.
    assert {remediate.route, accept.route, escalate.route} == set(Route)


def test_each_route_has_a_grounded_rationale() -> None:
    # The rationale names the decisive signals (the audit trail the §3 policy promises).
    remediate = triage(_signals(0.83, SeamClassification.CLEAN))
    assert "remediat" in remediate.rationale.lower()
    accept = triage(_signals(0.0, SeamClassification.BOUNDARY))
    assert "accept" in accept.rationale.lower()
    escalate = triage(_signals(0.5, SeamClassification.OPEN))
    assert "escalat" in escalate.rationale.lower()


# --- same-combination determinism (so the decision replays) -------------------


def test_same_combination_gives_the_same_route() -> None:
    # Same (rate, seam, severity) → same route: the policy is a pure function of the
    # observed state, so the recorded decision replays identically (MB-00 §4).
    a = triage(_signals(0.42, SeamClassification.CLEAN, FindingSeverity.MEDIUM))
    b = triage(_signals(0.42, SeamClassification.CLEAN, FindingSeverity.MEDIUM))
    assert a == b


# --- the policy's specific cells (transparent, MB-00 §3) ----------------------


def test_high_severity_escalates_regardless_of_rate_or_seam() -> None:
    # A severe finding warrants human eyes regardless of rate (MB-00 §3) — even at a
    # zero rate on a boundary seam.
    for rate in (0.0, 0.5, 1.0):
        for seam in SeamClassification:
            assert (
                route_for(_signals(rate, seam, FindingSeverity.HIGH)) == Route.ESCALATE
            )


def test_below_the_action_floor_is_accepted() -> None:
    # Below the floor, a non-severe finding is contained on rate grounds — for any seam.
    below = ACTION_FLOOR - 0.01
    for seam in SeamClassification:
        assert route_for(_signals(below, seam, FindingSeverity.LOW)) == Route.ACCEPT


def test_clean_above_floor_remediates_and_boundary_accepts() -> None:
    above = ACTION_FLOOR + 0.01
    assert route_for(_signals(above, SeamClassification.CLEAN)) == Route.REMEDIATE
    assert route_for(_signals(above, SeamClassification.BOUNDARY)) == Route.ACCEPT
    assert route_for(_signals(above, SeamClassification.OPEN)) == Route.ESCALATE


# --- parity: the agent's value enums must not drift from the real signals ------


def test_seam_classification_has_value_parity_with_seam_result() -> None:
    # The agent carries its OWN seam enum (so it imports nothing on the detection path,
    # MB-00 §4). This pins its values to the real framework SeamResult so it can never
    # silently drift — mechanical enforcement over a written rule.
    assert {c.value for c in SeamClassification} == {r.value for r in SeamResult}


def test_finding_severity_has_value_parity_with_fatf_severity() -> None:
    # Likewise the agent's severity enum is pinned to the real FATF Severity by value.
    assert {s.value for s in FindingSeverity} == {s.value for s in Severity}


@pytest.mark.parametrize("route", list(Route))
def test_routes_are_the_three_documented_actions(route: Route) -> None:
    assert route.value in {"remediate", "accept", "escalate"}
    assert len(Route) == 3
