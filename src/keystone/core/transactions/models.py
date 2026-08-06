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


# Identifier patterns — ADDITIVE (ADR-0037). Each accepts BOTH the legacy synthetic
# shape AND the ISO 20022 shape, so the model is ISO-CAPABLE without being ISO-shaped:
# every existing `TXN-######` / `ACC-####` fixture still validates unchanged, and the
# generator still emits those shapes. A misformed id still fails loud.
#
# KEEP IN SYNC with the narrative id tokenizer at
# `keystone.core.reporting.facts._ID_RE`. That regex must strip from report prose the
# same identifiers this one admits, or an id's digit-run is parsed as a phantom amount
# and the faithfulness guard silently falls back to the template narrative (Trap 1,
# pinned by `tests/test_faithfulness_guard.py`). The two are deliberately NOT identical
# — see the note at that site for why a prose tokenizer must be narrower — but they
# must be changed together. See ADR-0037.

# `id`: legacy `TXN-<6 digits>`, or an ISO 20022 EndToEndId / InstrId / MsgId. ISO
# permits up to 35 characters from [A-Za-z0-9/-?:().,'+ ] (`Max35Text`). Anchored on an
# alphanumeric at BOTH ends so empty, all-punctuation, and leading/trailing-whitespace
# ids are still rejected. NOTE the 35-char ceiling is ISO's own: a UUID MsgId fits only
# in its 32-char hex form — the canonical hyphenated UUID is 36 chars and is therefore
# NOT a valid Max35Text MsgId (asserted both ways in `tests/test_transactions.py`).
_ID_RE = re.compile(
    r"^(?=.{1,35}$)[A-Za-z0-9](?:[A-Za-z0-9/\-?:().,'+ ]*[A-Za-z0-9])?$"
)

# Accounts: legacy `ACC-<4 digits>`, or an IBAN (2 alpha country + 2 check digits + up
# to 30 alphanumeric, ISO 13616). An alternation rather than a charset class, because
# both shapes are strictly structured — this keeps the screen positive, not permissive.
_ACCOUNT_RE = re.compile(r"^(?:ACC-\d{4}|[A-Za-z]{2}\d{2}[A-Za-z0-9]{1,30})$")


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
            raise ValueError(
                f"id {self.id!r} is not a valid identifier: expected the legacy "
                "'TXN-<6 digits>' shape or an ISO 20022 EndToEndId/InstrId/MsgId "
                "(1-35 chars from [A-Za-z0-9/-?:().,'+ ], starting and ending "
                "alphanumeric)"
            )
        for account in (self.sender_account, self.recipient_account):
            if not _ACCOUNT_RE.match(account):
                raise ValueError(
                    f"account {account!r} is not a valid account identifier: expected "
                    "the legacy 'ACC-<4 digits>' shape or an IBAN (2 alpha country "
                    "code + 2 check digits + up to 30 alphanumeric)"
                )
        if self.sender_account == self.recipient_account:
            raise ValueError(
                f"sender and recipient must differ ({self.sender_account})"
            )
        return self


# --------------------------------------------------------------------------- #
# The untrusted-channel registry                                              #
# --------------------------------------------------------------------------- #
# SINGLE SOURCE OF TRUTH for the free-text fields a financial-crime detector must
# NEVER read. `keystone.assurance.framework.project_financial` blanks every name in
# this set before handing a stream to any detector, so the independence guarantee is
# driven from here rather than from a hard-coded field name.
#
# Lives in the core, co-located with the model it describes: the set of untrusted
# fields is a property of `Transaction` itself, and the core may not import the edge
# (import-linter). The edge consumer imports inward, which is legal.
#
# ADDING A FREE-TEXT FIELD TO `Transaction` REQUIRES ADDING IT HERE. A field absent
# from this set is one the detector can read — that is the whole invariant. The guard
# below rejects names that are not real, `str`-typed model fields; it cannot detect a
# free-text field someone forgot to register (see ADR-0036).
UNTRUSTED_CHANNELS: frozenset[str] = frozenset({"memo"})


def _validate_untrusted_channels() -> None:
    """Fail loudly at import if the registry names a field that cannot be stripped.

    `ValueError`, not `assert`: this must survive `python -O`, where asserts are
    stripped and a misregistered channel would silently stop being blanked.
    """
    for name in sorted(UNTRUSTED_CHANNELS):
        field = Transaction.model_fields.get(name)
        if field is None:
            raise ValueError(
                f"UNTRUSTED_CHANNELS names {name!r}, which is not a field of "
                f"Transaction (fields: {sorted(Transaction.model_fields)})"
            )
        if field.annotation is not str:
            raise ValueError(
                f"UNTRUSTED_CHANNELS names {name!r}, whose type is "
                f"{field.annotation!r}; only str-typed (free-text) fields can be "
                "blanked to ''"
            )


_validate_untrusted_channels()
