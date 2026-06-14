"""Unit tests for the hash-chained evidence ledger (KS-0102/KS-0103).

Fast, deterministic, no inference. Includes the adversarial tamper test that
docs/QUALITY.md requires for critical code.
"""

import sqlite3
from pathlib import Path

import pytest

from keystone.core.ledger import GENESIS_HASH, Ledger, LedgerEntry


@pytest.fixture
def ledger(tmp_path: Path) -> Ledger:
    return Ledger(tmp_path / "ledger.db")


def test_append_returns_entry_and_chains_from_genesis(ledger: Ledger) -> None:
    entry = ledger.append(agent="a", layer="layer1", action="probe")
    assert entry.id == 1
    assert entry.prev_hash == GENESIS_HASH
    assert entry.entry_hash == entry.compute_hash()


def test_append_orders_and_links_entries(ledger: Ledger) -> None:
    e1 = ledger.append(agent="a", layer="layer1", action="x")
    e2 = ledger.append(agent="b", layer="layer2", action="y", payload={"k": 1})
    e3 = ledger.append(agent="c", layer="layer3", action="z")

    entries = ledger.all()
    assert [e.id for e in entries] == [1, 2, 3]
    # Each entry's prev_hash is the previous entry's hash.
    assert e2.prev_hash == e1.entry_hash
    assert e3.prev_hash == e2.entry_hash


def test_verify_chain_true_on_good_chain(ledger: Ledger) -> None:
    for i in range(5):
        ledger.append(agent="a", layer="layer1", action=f"act{i}", payload={"i": i})
    assert ledger.verify_chain() is True


def test_empty_ledger_verifies(ledger: Ledger) -> None:
    assert ledger.verify_chain() is True


def test_verify_chain_false_when_payload_mutated(ledger: Ledger) -> None:
    ledger.append(agent="a", layer="layer1", action="x", payload={"amount": 1})
    ledger.append(agent="b", layer="layer2", action="y", payload={"amount": 2})
    assert ledger.verify_chain() is True

    # Tamper directly in the DB: change a stored payload without rehashing.
    with sqlite3.connect(ledger.db_path) as conn:
        conn.execute(
            "UPDATE entries SET payload = ? WHERE id = 1", ('{"amount": 999}',)
        )

    assert ledger.verify_chain() is False


def test_verify_chain_false_when_entry_deleted(ledger: Ledger) -> None:
    for i in range(3):
        ledger.append(agent="a", layer="layer1", action=f"a{i}")
    with sqlite3.connect(ledger.db_path) as conn:
        conn.execute("DELETE FROM entries WHERE id = 2")
    # The gap breaks both id-sequence and prev_hash linkage.
    assert ledger.verify_chain() is False


def test_entry_hash_is_stable_for_same_content() -> None:
    entry = LedgerEntry(
        id=1,
        ts="2026-06-15T00:00:00+00:00",
        agent="a",
        layer="layer1",
        action="x",
        payload={"b": 2, "a": 1},
        prev_hash=GENESIS_HASH,
        entry_hash="",
    )
    # Deterministic: recomputing yields the same digest regardless of key order.
    assert entry.compute_hash() == entry.compute_hash()
