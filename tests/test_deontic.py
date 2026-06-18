"""Tests for deterministic deontic-strength classification (KS-0206).

Fast, pure, no LLM/network. Pins the tiered classifier and the asymmetric-caution
drift detector the phrasing guard relies on, including the regression fixture
(hard-law "shall" -> "should"), the uncertain-on-strong case, the HARD_LAW
cross-check, and the chosen scope line (within-advisory drift is acceptable).
"""

from __future__ import annotations

import pytest

from keystone.core.deontic import Tier, classify, detect_modal_drift
from keystone.core.obligations import Modality

HARD = Modality.HARD_LAW
SELF = Modality.SELF_CERTIFICATION


# --- tiered classification ----------------------------------------------------


@pytest.mark.parametrize(
    ("text", "tier"),
    [
        ("The entity shall do X.", Tier.STRONG),
        ("The entity must do X.", Tier.STRONG),
        ("The entity is required to do X.", Tier.STRONG),
        ("This is mandatory.", Tier.STRONG),
        ("The entity should do X.", Tier.MEDIUM),
        ("The entity ought to do X.", Tier.MEDIUM),
        ("This is recommended.", Tier.MEDIUM),
        ("The entity may do X.", Tier.WEAK),
        ("The entity can do X.", Tier.WEAK),
        ("Entities are encouraged to do X.", Tier.WEAK),
        ("A data principal has the right to a summary.", Tier.UNCLASSIFIED),
    ],
)
def test_classify_tiers(text: str, tier: Tier) -> None:
    assert classify(text) is tier


def test_highest_tier_wins() -> None:
    # "must" (STRONG) dominates "should" (MEDIUM) in the same text.
    assert classify("It must be anchored; systems should be reliable.") is Tier.STRONG


def test_negated_binding_is_not_strong() -> None:
    assert classify("This is a recommendation, not a binding direction.") is Tier.MEDIUM


def test_requirement_noun_is_not_strong() -> None:
    assert classify("It is not a mandatory requirement.") is Tier.UNCLASSIFIED


# --- drift detection (asymmetric caution) -------------------------------------


def test_regression_shall_to_should_is_drift() -> None:
    # The fixture the guard exists for.
    assert detect_modal_drift(
        "Systems shall log events.", "Systems should log events.", HARD
    )


def test_strong_preserved_is_not_drift() -> None:
    assert not detect_modal_drift(
        "Systems shall log events.", "Systems must log events.", HARD
    )


def test_strengthening_advisory_to_binding_is_drift() -> None:
    assert detect_modal_drift(
        "Entities are encouraged to define responsibilities.",
        "Entities must define responsibilities.",
        SELF,
    )


def test_uncertain_on_strong_falls_back() -> None:
    # STRONG source, phrased drops the modal verb entirely -> cannot confirm force
    # -> drift (via the STRONG XOR), even on a non-hard-law node.
    assert detect_modal_drift(
        "Systems shall log events.", "Systems log events automatically.", SELF
    )


def test_hard_law_reading_advisory_is_drift_even_if_source_unclassified() -> None:
    # Source has no modal verb; HARD_LAW node phrased advisory -> cross-check drift.
    assert detect_modal_drift(
        "A data principal has the right to obtain a summary.",
        "A data principal may obtain a summary.",
        HARD,
    )


def test_within_advisory_drift_is_accepted_off_hard_law() -> None:
    # Chosen scope line: should <-> may on a non-hard-law node is NOT flagged.
    assert not detect_modal_drift("Entities should do X.", "Entities may do X.", SELF)


def test_both_unclassified_non_strong_passes() -> None:
    # Reachable only because the source is non-STRONG (the XOR guards #3).
    assert not detect_modal_drift(
        "The board reviews policies.", "The board examines policies.", SELF
    )


@pytest.mark.parametrize(
    ("source", "phrased", "modality", "expected"),
    [
        ("must X", "must X", HARD, False),  # preserved
        ("should X", "must X", SELF, True),  # strengthen
        ("must X", "should X", SELF, True),  # weaken
        ("must X", "X happens", SELF, True),  # uncertain-on-strong
        ("should X", "may X", SELF, False),  # within-advisory, accepted
        ("right to X", "may X", HARD, True),  # hard-law reads advisory
    ],
)
def test_drift_truth_table(
    source: str, phrased: str, modality: Modality, expected: bool
) -> None:
    assert detect_modal_drift(source, phrased, modality) is expected
