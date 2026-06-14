"""Hash-chained evidence ledger (deterministic core).

Public surface: the `Ledger` store, the `LedgerEntry` model, the `GENESIS_HASH`
constant, and env helpers for locating the ledger. No LLM or network deps.

The ledger location is configured by `KEYSTONE_LEDGER_DB` (default
`keystone-ledger.db` in the working directory).
"""

from __future__ import annotations

import os

from .ledger import Ledger
from .models import GENESIS_HASH, LedgerEntry

__all__ = [
    "DEFAULT_DB_PATH",
    "GENESIS_HASH",
    "Ledger",
    "LedgerEntry",
    "ledger_db_path",
    "open_ledger",
]

DEFAULT_DB_PATH = "keystone-ledger.db"


def ledger_db_path() -> str:
    """Path to the ledger DB, from `KEYSTONE_LEDGER_DB` or the default."""
    return os.environ.get("KEYSTONE_LEDGER_DB", DEFAULT_DB_PATH)


def open_ledger() -> Ledger:
    """Open the env-configured ledger."""
    return Ledger(ledger_db_path())
