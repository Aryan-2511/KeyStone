"""Pydantic models for the shared control library (KS-0202, ADR-0012 §5).

Deterministic core (ADR-0008): no LLM, no network. The control library is its
own data file (Option A); obligations reference controls by `control_id`. Each
control is defined at its natural granularity — the smallest coherent control
that obligations genuinely share — and is keyed to the ISO/IEC 42001 + FATF +
NIST AI RMF spine. Fail-loud invariants mirror `keystone.core.obligations`.
"""

from __future__ import annotations

import enum
import re
from typing import Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class Framework(enum.StrEnum):
    """The control spine the library is keyed to (ADR-0012)."""

    ISO_42001 = "ISO_42001"
    FATF = "FATF"
    NIST_AI_RMF = "NIST_AI_RMF"


# Locked id pattern: CTL-<DOMAIN>-<NN> (e.g. "CTL-GOV-01"). The domain segment is
# a short uppercase mnemonic; the number disambiguates controls within a domain.
_ID_RE = re.compile(r"^CTL-[A-Z]+-\d{2}$")


class SpineMapping(BaseModel):
    """A single mapping from a control to a framework provision (ADR-0012)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    framework: Framework
    reference: str

    @field_validator("reference")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must be non-empty")
        return value


class Control(BaseModel):
    """One shared control that obligations crosswalk onto."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    spine: list[SpineMapping]

    @field_validator("title", "description")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must be non-empty")
        return value

    @model_validator(mode="after")
    def _check(self) -> Self:
        if not _ID_RE.match(self.id):
            raise ValueError(f"id {self.id!r} must match {_ID_RE.pattern}")
        if not self.spine:
            raise ValueError(f"control {self.id!r} must map to at least one framework")
        return self
