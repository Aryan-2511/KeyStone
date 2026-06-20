"""Pydantic models for the synthetic transaction substrate (KS-0401, Layer 1).

Deterministic core (ADR-0008): no LLM, no network. This is the DATA LAYER all of
Layer 1 operates on — a typed transaction. It carries NO fraud labels (detection
is KS-0402's job) and NO seam wiring (KS-0403 plants the exploit), but it is
shaped so both are possible:

- a free-text `memo` field with UNTRUSTED-DATA semantics — the same physical seam
  the Layer-2 agent trusted, where KS-0403 will later plant the canonical exploit;
- account ids + amount + timestamp + type, enough for FATF typologies (e.g. a
  structuring / rapid-movement cluster) to be catchable on financial-crime grounds
  ALONE, independent of any memo content.

Fail-loud invariants mirror `keystone.core.obligations` / `keystone.core.ledger`.
"""

from __future__ import annotations

import datetime
import enum
import re
from typing import Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class Currency(enum.StrEnum):
    """Synthetic settlement currencies."""

    USD = "USD"
    EUR = "EUR"
    INR = "INR"
    GBP = "GBP"


class TransactionType(enum.StrEnum):
    """The movement type — FATF typologies read this alongside amount/timing."""

    TRANSFER = "TRANSFER"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    PAYMENT = "PAYMENT"


# Stable id patterns: TXN-<6 digits>, accounts ACC-<4 digits>. A misformed id fails.
_ID_RE = re.compile(r"^TXN-\d{6}$")
_ACCOUNT_RE = re.compile(r"^ACC-\d{4}$")


class Transaction(BaseModel):
    """One synthetic transaction — the Layer-1 substrate record."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    timestamp: datetime.datetime
    sender_account: str
    recipient_account: str
    amount: float
    currency: Currency
    tx_type: TransactionType
    # Free-text, UNTRUSTED data. Default empty; carries arbitrary text so KS-0403
    # can plant the canonical memo exploit here (the L2↔L1 seam locus). Not wired now.
    memo: str = ""

    @field_validator("amount")
    @classmethod
    def _positive_amount(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("amount must be positive")
        return value

    @model_validator(mode="after")
    def _check(self) -> Self:
        if not _ID_RE.match(self.id):
            raise ValueError(f"id {self.id!r} must match {_ID_RE.pattern}")
        for account in (self.sender_account, self.recipient_account):
            if not _ACCOUNT_RE.match(account):
                raise ValueError(
                    f"account {account!r} must match {_ACCOUNT_RE.pattern}"
                )
        if self.sender_account == self.recipient_account:
            raise ValueError(
                f"sender and recipient must differ ({self.sender_account})"
            )
        return self
