"""Guarded SAR/STR narrative generation (KS-0404, LLM edge).

The LLM edge phrases ONLY the human-readable narrative of a regulator report from
the deterministic `ReportFacts` (the system of record assembled in
`keystone.core.reporting`). It MUST NOT introduce or alter any fact.

Same fall-back-not-fail discipline as the deontic phrasing guard (KS-0206): the
model drafts the narrative, the deterministic `narrative_is_faithful` check
(core) verifies it adds no number / id / typology absent from the facts, and on
ANY drift the edge falls back to the always-faithful `template_narrative` — a
regulator filing is never emitted with a hallucinated figure, human sign-off
notwithstanding. Inference goes through the one allowed seam,
`keystone.llm.inference` (ADR-0008: only the edge calls an LLM).
"""

from __future__ import annotations

from dataclasses import dataclass

from keystone.core.fatf import Finding
from keystone.core.reporting import (
    Report,
    ReportFacts,
    assemble_facts,
    narrative_is_faithful,
    template_narrative,
)
from keystone.core.transactions import Transaction

from .inference import Backend, complete

# `/no_think` disables reasoning; the rest is the faithfulness contract.
NARRATIVE_SYSTEM = (
    "/no_think\n"
    "You are drafting the narrative paragraph of a suspicious-transaction report. "
    "Write 2-4 sentences of plain regulatory English describing the suspicious "
    "activity. Use ONLY the figures, account ids, transaction ids, dates, and "
    "typology provided below — do NOT add, remove, round, or alter any number, id, "
    "date, or typology, and do NOT invent any detail. Output ONLY the narrative."
)


@dataclass(frozen=True)
class GuardedNarrative:
    """Result of narrative generation: the text, and whether it fell back.

    `text` is the model's narrative when faithful, or the deterministic
    `template_narrative` when the faithfulness guard caught drift. `fell_back` is
    True in the latter case so a report (and the ledger) can mark it.
    """

    text: str
    fell_back: bool


def _facts_prompt(facts: ReportFacts) -> str:
    """Render the structured facts as the model prompt (the only allowed inputs)."""
    return (
        f"Typology: {facts.typology}\n"
        f"Account under review: {facts.account}\n"
        f"Transaction count: {facts.transaction_count}\n"
        f"Transaction ids: {', '.join(facts.transaction_ids)}\n"
        f"Total amount: {facts.total_amount} {facts.currency}\n"
        f"Period: {facts.period_start:%Y-%m-%d %H:%M} to "
        f"{facts.period_end:%Y-%m-%d %H:%M}\n"
        f"Detection rationale: {facts.rationale}\n"
    )


def generate_narrative(
    facts: ReportFacts, *, backend: Backend | None = None
) -> GuardedNarrative:
    """Draft the report narrative from `facts`, guarded against invented facts.

    Calls the inference seam to phrase the facts, then keeps the result only if it
    is faithful (`narrative_is_faithful`); otherwise falls back to the deterministic
    template. Never mutates the facts or any core data. `backend` is injectable (the
    fast gate uses a fake one).
    """
    drafted = complete(
        _facts_prompt(facts), system=NARRATIVE_SYSTEM, backend=backend
    ).strip()
    if drafted and narrative_is_faithful(drafted, facts):
        return GuardedNarrative(text=drafted, fell_back=False)
    return GuardedNarrative(text=template_narrative(facts), fell_back=True)


def draft_report(
    finding: Finding,
    transactions: list[Transaction],
    *,
    backend: Backend | None = None,
) -> Report:
    """Assemble facts (core) + a guarded narrative (edge) into a DRAFT report.

    The report starts DRAFT — the caller signs it off (oversight) and records it.
    """
    facts = assemble_facts(finding, transactions)
    narrative = generate_narrative(facts, backend=backend)
    return Report(
        facts=facts,
        narrative=narrative.text,
        narrative_fell_back=narrative.fell_back,
    )
