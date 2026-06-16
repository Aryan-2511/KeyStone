"""Pydantic models for the curated regulatory obligation graph.

Deterministic core (ADR-0008): no LLM, no network. The schema, enums, field
rules, and fail-loud invariants are locked by ADR-0012. `summary` is the
curated, human-written source text and the system of record; KS-0204's LLM
phrasing is a separate, edge-side transform that must never write back here.
"""

from __future__ import annotations

import datetime
import enum
import re
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Instrument(enum.StrEnum):
    """The regulatory instruments the graph spans (ADR-0012)."""

    EU_AI_ACT = "EU_AI_ACT"
    DORA = "DORA"
    DPDP_ACT = "DPDP_ACT"
    DPDP_RULES_2025 = "DPDP_RULES_2025"
    RBI_GUIDANCE = "RBI_GUIDANCE"
    PMLA_FIU_IND = "PMLA_FIU_IND"


class Modality(enum.StrEnum):
    """Enforcement modality — feeds the KS-0203 contrast."""

    HARD_LAW = "HARD_LAW"
    SELF_CERTIFICATION = "SELF_CERTIFICATION"


class Jurisdiction(enum.StrEnum):
    """Jurisdiction — feeds Phase 4's pluggable jurisdictions."""

    EU = "EU"
    INDIA = "INDIA"


# Instrument -> stable id prefix (ADR-0012; EUAI is the ADR's worked example).
# The id encodes its instrument so a misfiled node fails validation.
_ID_PREFIX: dict[Instrument, str] = {
    Instrument.EU_AI_ACT: "EUAI",
    Instrument.DORA: "DORA",
    Instrument.DPDP_ACT: "DPDPA",
    Instrument.DPDP_RULES_2025: "DPDPR",
    Instrument.RBI_GUIDANCE: "RBI",
    Instrument.PMLA_FIU_IND: "PMLA",
}

# Locked id pattern from ADR-0012: OBL-<PREFIX>-<NNN>.
_ID_RE = re.compile(r"^OBL-[A-Z0-9]+-\d{3}$")


class Citation(BaseModel):
    """A structured legal citation (ADR-0012) — gateable, not free text."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    instrument: Instrument
    provision: str
    title: str
    url: str | None = None
    retrieved: datetime.date | None = None

    @field_validator("provision", "title")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must be non-empty")
        return value


class Obligation(BaseModel):
    """One curated regulatory obligation node."""

    model_config = ConfigDict(extra="forbid")

    id: str
    instrument: Instrument
    citation: Citation
    summary: str
    enforcement_modality: Modality
    jurisdiction: Jurisdiction
    control_ids: list[str] = Field(default_factory=list)

    @field_validator("summary")
    @classmethod
    def _summary_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("summary must be non-empty")
        return value

    @model_validator(mode="after")
    def _check_consistency(self) -> Self:
        if not _ID_RE.match(self.id):
            raise ValueError(f"id {self.id!r} must match {_ID_RE.pattern}")
        expected_prefix = _ID_PREFIX[self.instrument]
        actual_prefix = self.id.split("-")[1]
        if actual_prefix != expected_prefix:
            raise ValueError(
                f"id {self.id!r} prefix must be {expected_prefix!r} "
                f"for instrument {self.instrument}"
            )
        if self.citation.instrument != self.instrument:
            raise ValueError(
                "citation.instrument "
                f"({self.citation.instrument}) must equal "
                f"obligation.instrument ({self.instrument})"
            )
        return self
