"""Typed findings for the FATF typology detection engine (KS-0402, Layer 1).

Deterministic core (ADR-0008): no LLM, no network. A `Finding` records WHY a
transaction (or cluster) is suspicious on FINANCIAL-CRIME grounds — amounts,
timing, velocity, account relationships. It deliberately has NO memo field: the
detector is memo-BLIND, which is what keeps the KS-0403 seam's two detections
(AML here, prompt-injection in the assurance loop) independent.
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class Typology(enum.StrEnum):
    """The FATF financial-crime patterns this engine detects."""

    STRUCTURING = "STRUCTURING"
    RAPID_MOVEMENT = "RAPID_MOVEMENT"
    LARGE_TRANSFER = "LARGE_TRANSFER"
    # KS-0605 (P5): a payment whose DESTINATION is on a standing flagged-destination
    # list (sanctions-style screening). A new SIGNAL TYPE — list membership, not an
    # intrinsic money pattern — but the same memo-blind, financial-signal-only contract.
    UNAUTHORIZED_RECIPIENT = "UNAUTHORIZED_RECIPIENT"


class Severity(enum.StrEnum):
    """Finding severity for triage."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Finding(BaseModel):
    """One suspicious-activity finding, justified by financial signals only."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    typology: Typology
    severity: Severity
    account: str
    transaction_ids: tuple[str, ...]
    # The financial signal that tripped the rule (counts/amounts/timing) — never
    # memo content. Kept structured so the ledger entry is auditable.
    signal: dict[str, Any]
    rationale: str
