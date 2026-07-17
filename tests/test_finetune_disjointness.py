"""The credibility test for FINETUNE-SPIKE-01: the committed data is provably clean.

A fine-tune result is only meaningful if the training set is disjoint from the frozen
held-out eval. These tests assert that on the COMMITTED artifacts (not a fresh in-memory
build), so the guarantee travels with the repo:

- ZERO training rows contaminate the held-out set (band membership OR near-duplicate).
- Every training rate is outside the reserved threshold band.
- Every label — training AND held-out — equals ``route_for`` (the sole labeler; catches
  any policy drift silently invalidating the frozen labels).
- The committed training set reproduces the deterministic generator (no hand-editing).

If any of these fail, the spike's result would be self-deceptive — fix the generator, never
these assertions or the protocol.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from keystone.agents.triage import route_for
from keystone.finetune.dataset import build_heldout, build_training
from keystone.finetune.protocol import (
    RESERVED_BAND_HIGH,
    RESERVED_BAND_LOW,
    Case,
    case_to_json,
    contaminates_heldout,
    in_reserved_band,
    read_cases_jsonl,
    to_chat_record,
)

_DATA = Path(__file__).resolve().parents[1] / "src" / "keystone" / "finetune" / "data"
HELDOUT_PATH = _DATA / "heldout_eval.jsonl"
TRAIN_PATH = _DATA / "train.jsonl"


@pytest.fixture(scope="module")
def heldout() -> list[Case]:
    return read_cases_jsonl(HELDOUT_PATH)


@pytest.fixture(scope="module")
def train() -> list[Case]:
    return read_cases_jsonl(TRAIN_PATH)


def test_protocol_band_edges_are_the_quoted_values() -> None:
    # The whole credibility argument (and the paper) quotes this band; pin it here.
    assert (RESERVED_BAND_LOW, RESERVED_BAND_HIGH) == (0.05, 0.20)


def test_zero_training_rows_contaminate_heldout(
    train: list[Case], heldout: list[Case]
) -> None:
    # THE assertion the whole spike rests on.
    leaks = [c for c in train if contaminates_heldout(c.signals, heldout)]
    assert leaks == [], f"{len(leaks)} contaminated training rows, e.g. {leaks[:3]}"


def test_no_training_rate_in_reserved_band(train: list[Case]) -> None:
    in_band = [
        c.signals.failure_rate
        for c in train
        if in_reserved_band(c.signals.failure_rate)
    ]
    assert in_band == [], f"training rates inside the reserved band: {in_band[:5]}"


def test_chat_records_preserve_signals_and_stay_disjoint(
    train: list[Case], heldout: list[Case]
) -> None:
    # train_chat.jsonl is generated (not committed — it embeds the full system prompt ×465).
    # Verify the chat record for each committed train case carries the SAME signals (no drift)
    # and is disjoint — so the file, whenever `make finetune-data` produces it, is clean too.
    for case in train:
        record = to_chat_record(case)
        sig = record["signals"]
        assert isinstance(sig, dict)
        assert sig["failure_rate"] == case.signals.failure_rate
        assert sig["seam_result"] == case.signals.seam_result.value
        assert sig["severity"] == case.signals.severity.value
        assert not contaminates_heldout(case.signals, heldout)


def test_training_labels_match_policy(train: list[Case]) -> None:
    for case in train:
        assert case.route == route_for(case.signals), case.name


def test_heldout_labels_match_policy(heldout: list[Case]) -> None:
    # Frozen labels must still equal the policy — a route_for change would invalidate them.
    for case in heldout:
        assert case.route == route_for(case.signals), case.name


def test_committed_data_reproduces_the_generator(
    train: list[Case], heldout: list[Case]
) -> None:
    # The committed artifacts must be exactly what the deterministic builders produce.
    assert [case_to_json(c) for c in heldout] == [
        case_to_json(c) for c in build_heldout()
    ]
    regenerated = build_training(build_heldout())
    assert [case_to_json(c) for c in train] == [case_to_json(c) for c in regenerated]


def test_heldout_concentrates_on_the_threshold_band(heldout: list[Case]) -> None:
    # The point of the held-out set: it lives where general 3B failed (the 0.10 threshold).
    in_band = sum(1 for c in heldout if c.in_band)
    assert in_band >= len(heldout) * 0.8


def test_training_is_route_balanced(train: list[Case]) -> None:
    counts = {
        r: sum(1 for c in train if c.route is r) for r in {c.route for c in train}
    }
    assert len(counts) == 3  # all three routes present
    assert max(counts.values()) - min(counts.values()) <= 1  # balanced by construction
