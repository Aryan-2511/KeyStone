"""Regulator report object, format adapters, sign-off, and ledger (KS-0404).

Deterministic core (ADR-0008): no LLM, no network. A `Report` is the assembled
`ReportFacts` + a narrative + a draft/signed status. FORMAT-AGNOSTIC core: the
facts are assembled once and rendered by adapters — FINnet 2.0 (India, primary)
and goAML (secondary, lighter) — proving the "one fact model, many regulator
formats" pluggable-connector design. The adapters MODEL known STR/report fields
and clearly MARK placeholders; they do not fabricate an official schema.

The report is DRAFTED, never auto-filed: an explicit `sign_off` moves it
draft → signed (oversight in the loop), and both events are recorded to the
hash-chained evidence ledger.
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, ConfigDict

from keystone.core.ledger import Ledger, LedgerEntry, open_ledger

from .facts import ReportFacts

LEDGER_AGENT = "report-generator"
LEDGER_LAYER = "L1"

# Placeholder sentinels — values a real filing's reporting entity must supply.
_PLACEHOLDER = "<PLACEHOLDER>"


class ReportFormat(enum.StrEnum):
    """Supported regulator formats (FINnet primary, goAML second)."""

    FINNET = "FINNET"
    GOAML = "GOAML"


class ReportStatus(enum.StrEnum):
    """Human-checkpoint status: drafted, then signed off (never auto-filed)."""

    DRAFT = "DRAFT"
    SIGNED = "SIGNED"


class Report(BaseModel):
    """A drafted regulator report: facts + narrative + sign-off status."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    facts: ReportFacts
    narrative: str
    narrative_fell_back: bool
    status: ReportStatus = ReportStatus.DRAFT
    signed_by: str | None = None


def sign_off(report: Report, signer: str) -> Report:
    """Move a DRAFT report to SIGNED with the signer recorded (oversight step)."""
    return report.model_copy(
        update={"status": ReportStatus.SIGNED, "signed_by": signer}
    )


def to_finnet(report: Report) -> dict[str, Any]:
    """Render a report into a representative FINnet 2.0 (FIU-IND) STR structure.

    Models the known STR fields; reporting-entity values are PLACEHOLDERS the
    filing entity supplies. Not the literal official XML schema.
    """
    facts = report.facts
    return {
        "report_type": "STR",
        "schema_note": (
            "Representative model of FINnet 2.0 (FIU-IND) STR fields; "
            "reporting-entity values are placeholders, not an official schema."
        ),
        "reporting_entity": {"re_name": _PLACEHOLDER, "re_id": _PLACEHOLDER},
        "report_date": report.facts.period_end.date().isoformat(),
        "ground_of_suspicion": facts.typology,
        "suspicious_transactions": [
            {
                "transaction_id": tid,
                "account": facts.account,
                "amount": amount,
                "currency": facts.currency,
            }
            for tid, amount in zip(facts.transaction_ids, facts.amounts, strict=True)
        ],
        "total_amount": facts.total_amount,
        "narrative": report.narrative,
        "status": report.status.value,
        "signed_by": report.signed_by or _PLACEHOLDER,
    }


def to_goaml(report: Report) -> dict[str, Any]:
    """Render the SAME facts into a representative UN goAML report structure.

    The second adapter substantiates "pluggable": one fact model, another format.
    """
    facts = report.facts
    return {
        "report_code": "STR",
        "schema_note": (
            "Representative model of UN goAML report fields; "
            "rentity values are placeholders, not an official schema."
        ),
        "rentity_id": _PLACEHOLDER,
        "submission_date": report.facts.period_end.date().isoformat(),
        "report_indicator": facts.typology,
        "transactions": [
            {
                "transactionnumber": tid,
                "from_account": facts.account,
                "amount_local": amount,
                "currency_code": facts.currency,
            }
            for tid, amount in zip(facts.transaction_ids, facts.amounts, strict=True)
        ],
        "reason": report.narrative,
        "status": report.status.value,
    }


def render(report: Report, fmt: ReportFormat) -> dict[str, Any]:
    """Render a report in the requested format (the pluggable adapter switch)."""
    if fmt is ReportFormat.FINNET:
        return to_finnet(report)
    return to_goaml(report)


def record_report(
    report: Report, fmt: ReportFormat, *, ledger: Ledger | None = None
) -> LedgerEntry:
    """Record a drafted/signed report to the evidence ledger.

    Action is `report_drafted` or `report_signed` per status, so the ledger shows
    the human checkpoint. Carries the format, typology, implicated tx ids, the
    narrative, and whether the narrative fell back to the safe template.
    """
    led = ledger if ledger is not None else open_ledger()
    action = (
        "report_signed" if report.status is ReportStatus.SIGNED else "report_drafted"
    )
    return led.append(
        agent=LEDGER_AGENT,
        layer=LEDGER_LAYER,
        action=action,
        payload={
            "format": fmt.value,
            "typology": report.facts.typology,
            "account": report.facts.account,
            "transaction_ids": list(report.facts.transaction_ids),
            "total_amount": report.facts.total_amount,
            "currency": report.facts.currency,
            "narrative": report.narrative,
            "narrative_fell_back": report.narrative_fell_back,
            "status": report.status.value,
            "signed_by": report.signed_by,
        },
    )
