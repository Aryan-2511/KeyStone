"""Tests for deterministic deontic-strength classification (KS-0206).

Fast, pure, no LLM/network. Pins the modal classifier and the drift detector the
phrasing guard relies on, including the cases observed live (EU "shall"->"should"
weakening; RBI advisory body gaining "must"; advisory text that legitimately
carries "must" inside a non-binding wrapper).
"""

from __future__ import annotations

import pytest

from keystone.core.deontic import ModalProfile, drifts, modal_profile


def test_modal_profile_counts_binding() -> None:
    p = modal_profile("The entity must do X and shall do Y.")
    assert p.binding == 2
    assert p.advisory == 0


def test_modal_profile_counts_advisory() -> None:
    p = modal_profile("The entity should do X and may do Y.")
    assert p == ModalProfile(binding=0, advisory=2)


def test_negated_binding_is_not_counted_as_binding() -> None:
    # "not binding" / "not mandatory" signal advisory framing, not binding force.
    p = modal_profile("This is a recommendation, not a binding direction.")
    assert p.binding == 0


def test_must_not_prohibition_still_counts_as_binding() -> None:
    p = modal_profile("The entity must not process children's data.")
    assert p.binding == 1


def test_ambiguous_requirement_noun_not_counted() -> None:
    # "requirement" as a noun is excluded to keep BINDING precise.
    assert modal_profile("It is not a mandatory requirement.").binding == 0


# --- drift detection ----------------------------------------------------------


def test_no_drift_when_force_preserved() -> None:
    assert not drifts("Systems shall be robust.", "Systems must be robust.")


def test_weakening_binding_to_advisory_is_drift() -> None:
    # The EU AI Act case: "shall" -> "should".
    assert drifts("Systems shall log events.", "Systems should log events.")


def test_strengthening_advisory_to_binding_is_drift() -> None:
    # The RBI advisory-body case: source has no binding verb, reword adds "must".
    assert drifts(
        "Entities are encouraged to define responsibilities.",
        "Entities must define responsibilities.",
    )


def test_advisory_to_advisory_is_not_drift() -> None:
    assert not drifts("Systems should be reliable.", "Systems may be reliable.")


def test_binding_source_kept_binding_is_not_drift() -> None:
    # Advisory wrapper text whose curated source legitimately uses "must".
    assert not drifts(
        "Adoption must be anchored in trust; this is not a binding direction.",
        "Adoption must be rooted in trust; this is not binding.",
    )


@pytest.mark.parametrize(
    ("source", "candidate", "expected"),
    [
        ("must", "must", False),
        ("should", "must", True),  # strengthen
        ("must", "should", True),  # weaken
        ("should", "should", False),
    ],
)
def test_drift_truth_table(source: str, candidate: str, expected: bool) -> None:
    assert drifts(source, candidate) is expected
