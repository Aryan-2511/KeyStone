"""Pydantic model for evidence-ledger entries.

The ledger is part of the deterministic core: an entry's hash is a pure function
of its content and the previous entry's hash, so the whole chain is verifiable
without any LLM in the loop.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, Field

# Fixed genesis predecessor for the first entry.
GENESIS_HASH = "0" * 64


class LedgerEntry(BaseModel):
    """One append-only, hash-chained evidence record."""

    id: int
    ts: str
    agent: str
    layer: str
    action: str
    payload: dict[str, Any] = Field(default_factory=dict)
    prev_hash: str
    entry_hash: str

    def canonical_content(self) -> str:
        """Deterministic JSON of the hashed fields (everything but entry_hash)."""
        return json.dumps(
            {
                "id": self.id,
                "ts": self.ts,
                "agent": self.agent,
                "layer": self.layer,
                "action": self.action,
                "payload": self.payload,
                "prev_hash": self.prev_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    def compute_hash(self) -> str:
        """Recompute this entry's hash from its content + prev_hash."""
        digest = self.canonical_content() + self.prev_hash
        return hashlib.sha256(digest.encode("utf-8")).hexdigest()
