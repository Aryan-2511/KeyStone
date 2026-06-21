"""Report facts + the deterministic faithfulness guard (KS-0404, Layer 1 core).

Deterministic core (ADR-0008): no LLM, no network. This is the SYSTEM OF RECORD
for a regulator report: `assemble_facts` turns a FATF `Finding` + the implicated
`Transaction`s into structured facts (typology, ids, amounts, accounts, currency,
timestamps, totals, rationale). The LLM edge (KS-0404) phrases ONLY the narrative
from these facts; it must never invent or alter one.

The faithfulness GUARD lives here too because it is deterministic: a `template_
narrative` (the always-faithful safe floor, no LLM) and `narrative_is_faithful`,
which checks that every number / id / typology in a narrative is present in the
facts. The edge calls these and falls back to the template on any drift —
certainly-faithful over probably-faithful, mirroring the deontic guard (KS-0206).
A regulator filing with a hallucinated figure is exactly what this prevents; human
sign-off does NOT replace it.
"""

from __future__ import annotations

import datetime
import re

from pydantic import BaseModel, ConfigDict

from keystone.core.fatf import Finding, Typology
from keystone.core.transactions import Transaction


class ReportAssemblyError(Exception):
    """Raised when facts cannot be assembled (e.g. a finding implicates no txns)."""


class ReportFacts(BaseModel):
    """Structured, deterministic facts for a regulator report (system of record)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    typology: str
    severity: str
    account: str
    transaction_ids: tuple[str, ...]
    counterparties: tuple[str, ...]
    currency: str
    amounts: tuple[float, ...]
    total_amount: float
    transaction_count: int
    period_start: datetime.datetime
    period_end: datetime.datetime
    rationale: str


def assemble_facts(finding: Finding, transactions: list[Transaction]) -> ReportFacts:
    """Assemble report facts from a finding and the transactions it implicates.

    Deterministic: pulls the implicated transactions by id (order preserved),
    derives amounts/total/count/period/currency/counterparties from them, and takes
    typology/severity/account/rationale from the finding. Raises if the finding
    implicates no known transactions.
    """
    by_id = {t.id: t for t in transactions}
    implicated = [by_id[tid] for tid in finding.transaction_ids if tid in by_id]
    if not implicated:
        raise ReportAssemblyError(
            f"finding implicates no known transactions: {finding.transaction_ids}"
        )

    amounts = tuple(t.amount for t in implicated)
    timestamps = [t.timestamp for t in implicated]
    return ReportFacts(
        typology=finding.typology.value,
        severity=finding.severity.value,
        account=finding.account,
        transaction_ids=tuple(t.id for t in implicated),
        counterparties=tuple(dict.fromkeys(t.recipient_account for t in implicated)),
        currency=implicated[0].currency.value,
        amounts=amounts,
        total_amount=round(sum(amounts), 2),
        transaction_count=len(implicated),
        period_start=min(timestamps),
        period_end=max(timestamps),
        rationale=finding.rationale,
    )


def template_narrative(facts: ReportFacts) -> str:
    """A deterministic SAR/STR narrative from facts — the always-faithful floor.

    No LLM. Uses only values present in `facts`, so it passes
    `narrative_is_faithful` by construction (the safe fallback).
    """
    return (
        f"A {facts.typology} pattern was detected on account {facts.account}. "
        f"{facts.transaction_count} transactions totalling {facts.total_amount} "
        f"{facts.currency} occurred between "
        f"{facts.period_start:%Y-%m-%d %H:%M} and {facts.period_end:%Y-%m-%d %H:%M}. "
        f"{facts.rationale}"
    )


# Number/id tokenizers for the faithfulness check.
_NUMBER_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
_ID_RE = re.compile(r"\b(?:TXN|ACC)-\d+\b")


def _numbers(text: str) -> set[float]:
    # Strip ACC-/TXN- ids first: their digits are validated by the id check, not as
    # standalone amounts — so citing a real id never reads as an invented number.
    out: set[float] = set()
    for token in _NUMBER_RE.findall(_ID_RE.sub(" ", text)):
        out.add(round(float(token.replace(",", "")), 2))
    return out


def _ids(text: str) -> set[str]:
    return set(_ID_RE.findall(text))


def _allowed_numbers(facts: ReportFacts) -> set[float]:
    allowed = {round(a, 2) for a in facts.amounts}
    allowed.add(round(facts.total_amount, 2))
    allowed.add(float(facts.transaction_count))
    for moment in (facts.period_start, facts.period_end):
        allowed.update(
            float(part)
            for part in (
                moment.year,
                moment.month,
                moment.day,
                moment.hour,
                moment.minute,
            )
        )
    # The rationale is itself a core-supplied fact; its numbers are allowed.
    allowed |= _numbers(facts.rationale)
    return allowed


def _allowed_ids(facts: ReportFacts) -> set[str]:
    return (
        {facts.account}
        | set(facts.transaction_ids)
        | set(facts.counterparties)
        | _ids(facts.rationale)
    )


def narrative_is_faithful(narrative: str, facts: ReportFacts) -> bool:
    """True if `narrative` introduces no number, id, or typology absent from facts.

    Deterministic guard: every numeric value and every TXN-/ACC- id in the
    narrative must be present in the facts (including the rationale and the report
    period). A different FATF typology naming is also a violation. Used by the edge
    to decide whether to keep the LLM narrative or fall back to the template.
    """
    if not _numbers(narrative) <= _allowed_numbers(facts):
        return False
    if not _ids(narrative) <= _allowed_ids(facts):
        return False
    lowered = narrative.lower()
    for typology in Typology:
        if typology.value != facts.typology and typology.value.lower() in lowered:
            return False
    return True
