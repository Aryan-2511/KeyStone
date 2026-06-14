"""Append-only, hash-chained evidence ledger backed by SQLite.

Deterministic core. No LLM, no network. Each appended entry chains to the
previous entry's hash; `verify_chain()` recomputes every hash to detect
tampering (mutation, insertion, or deletion).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import GENESIS_HASH, LedgerEntry

_SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id        INTEGER PRIMARY KEY,
    ts        TEXT NOT NULL,
    agent     TEXT NOT NULL,
    layer     TEXT NOT NULL,
    action    TEXT NOT NULL,
    payload   TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    entry_hash TEXT NOT NULL
);
"""


class Ledger:
    """A SQLite-backed hash-chained ledger at a given path."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_entry(self, row: sqlite3.Row) -> LedgerEntry:
        return LedgerEntry(
            id=row["id"],
            ts=row["ts"],
            agent=row["agent"],
            layer=row["layer"],
            action=row["action"],
            payload=json.loads(row["payload"]),
            prev_hash=row["prev_hash"],
            entry_hash=row["entry_hash"],
        )

    def append(
        self,
        *,
        agent: str,
        layer: str,
        action: str,
        payload: dict[str, Any] | None = None,
    ) -> LedgerEntry:
        """Append one entry, chaining it to the current tail. Returns the entry."""
        with self._connect() as conn:
            tail = conn.execute(
                "SELECT id, entry_hash FROM entries ORDER BY id DESC LIMIT 1"
            ).fetchone()
            next_id = (tail["id"] + 1) if tail else 1
            prev_hash = tail["entry_hash"] if tail else GENESIS_HASH

            entry = LedgerEntry(
                id=next_id,
                ts=datetime.now(UTC).isoformat(),
                agent=agent,
                layer=layer,
                action=action,
                payload=payload or {},
                prev_hash=prev_hash,
                entry_hash="",
            )
            entry.entry_hash = entry.compute_hash()

            conn.execute(
                "INSERT INTO entries "
                "(id, ts, agent, layer, action, payload, prev_hash, entry_hash) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    entry.id,
                    entry.ts,
                    entry.agent,
                    entry.layer,
                    entry.action,
                    json.dumps(entry.payload, sort_keys=True, ensure_ascii=False),
                    entry.prev_hash,
                    entry.entry_hash,
                ),
            )
        return entry

    def all(self) -> list[LedgerEntry]:
        """Return every entry, ordered by id."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM entries ORDER BY id ASC").fetchall()
        return [self._row_to_entry(row) for row in rows]

    def verify_chain(self) -> bool:
        """Recompute the whole chain; return False on any tamper."""
        prev_hash = GENESIS_HASH
        expected_id = 1
        for entry in self.all():
            if entry.id != expected_id:
                return False
            if entry.prev_hash != prev_hash:
                return False
            if entry.compute_hash() != entry.entry_hash:
                return False
            prev_hash = entry.entry_hash
            expected_id += 1
        return True
