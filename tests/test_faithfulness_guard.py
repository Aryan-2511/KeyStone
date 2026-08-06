"""Regression fence for the report faithfulness guard's ID TOKENIZER (KS-0404).

The guard (`narrative_is_faithful`) rejects a narrative that introduces any number or
id absent from the facts. To do that it must first STRIP identifiers out of the text,
because an id's digit-run is not an amount: `core/reporting/facts.py::_numbers` runs
`_ID_RE.sub(" ", text)` before `_NUMBER_RE` ever sees the string.

That makes the id tokenizer a SILENT-FAILURE surface, and these tests are its fence:

    an id shape the tokenizer does not recognise
      -> its digits survive into `_NUMBER_RE`
      -> they read as a phantom amount absent from the facts
      -> `narrative_is_faithful` returns False
      -> the edge quietly falls back to the template narrative

Nothing raises. No existing assertion fails. The report still files — just always
with the deterministic template, with the LLM narrative silently discarded. The ISO
20022 migration makes exactly this happen the moment identifiers stop being
`TXN-######` / `ACC-####`, which is why the fence is planted BEFORE the widening.

These drive the real public entry point (`narrative_is_faithful` over a real
`ReportFacts`), never a reimplementation of the tokenizer.
"""

from __future__ import annotations

import datetime

import pytest

from keystone.core.reporting import ReportFacts, narrative_is_faithful

_T0 = datetime.datetime(2026, 3, 1, 12, 0, tzinfo=datetime.UTC)
_T1 = datetime.datetime(2026, 3, 1, 13, 30, tzinfo=datetime.UTC)

# An ISO 20022 IBAN (the shape `sender_account` / `recipient_account` take once the
# substrate is ISO-capable) and an EndToEndId-style payment reference (the shape `id`
# takes). Both carry long digit-runs that are NOT any amount in the facts below — so
# if the tokenizer fails to strip them, they surface as phantom amounts.
_IBAN = "DE89370400440532013000"
_END_TO_END_ID = "E2E-REF-778899"

# Legacy identifiers, for the baseline case. Same role, current shapes.
_LEGACY_ACCOUNT = "ACC-0004"
_LEGACY_TXN_ID = "TXN-000016"


def _facts(*, account: str, transaction_id: str, counterparty: str) -> ReportFacts:
    """A minimal, real `ReportFacts` parameterized by identifier shape.

    `ReportFacts` is the deterministic system of record and applies no id-format
    validation of its own, so the same helper serves both the legacy and the ISO case
    — which is what makes the two tests a like-for-like comparison.
    """
    return ReportFacts(
        typology="STRUCTURING",
        severity="HIGH",
        account=account,
        transaction_ids=(transaction_id,),
        counterparties=(counterparty,),
        currency="USD",
        amounts=(9011.52,),
        total_amount=9011.52,
        transaction_count=1,
        period_start=_T0,
        period_end=_T1,
        rationale="Structuring pattern detected on financial signals alone.",
    )


def test_faithful_narrative_with_legacy_ids_is_faithful() -> None:
    # BASELINE (passes today): with `TXN-######` / `ACC-####` the tokenizer strips both
    # ids, so only the real amount 9011.52 reaches the number check. This is the
    # behaviour the ISO case below must match — it pins what "working" looks like.
    facts = _facts(
        account=_LEGACY_ACCOUNT,
        transaction_id=_LEGACY_TXN_ID,
        counterparty="ACC-0023",
    )
    narrative = (
        f"A STRUCTURING pattern was detected on account {_LEGACY_ACCOUNT}. "
        f"Transaction {_LEGACY_TXN_ID} moved 9011.52 USD to ACC-0023."
    )
    assert narrative_is_faithful(narrative, facts) is True


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Trap 1: facts.py id-tokenizer does not strip ISO-shaped ids yet; "
        "fixed in commit 2 of this PR"
    ),
)
def test_faithful_narrative_with_iso_shaped_ids_is_faithful() -> None:
    # THE TRAP. This narrative is faithful by construction: every amount it cites
    # (9011.52) is in the facts, and every id it cites is in the facts. The ONLY
    # difference from the baseline above is the SHAPE of the identifiers.
    #
    # Against the current tokenizer this returns False, because `_ID_RE` matches only
    # `(?:TXN|ACC)-\d+`. The IBAN's "89370400440532013000" and the reference's "778899"
    # are therefore never stripped, `_NUMBER_RE` reads them as amounts, and the subset
    # check `_numbers(narrative) <= _allowed_numbers(facts)` fails.
    #
    # strict=True: the moment commit 2 widens the tokenizer this test PASSES, pytest
    # reports XPASS-as-failure, and the stale marker cannot be forgotten.
    facts = _facts(
        account=_IBAN,
        transaction_id=_END_TO_END_ID,
        counterparty="GB33BUKB20201555555555",
    )
    narrative = (
        f"A STRUCTURING pattern was detected on account {_IBAN}. "
        f"Transaction {_END_TO_END_ID} moved 9011.52 USD to "
        "GB33BUKB20201555555555."
    )
    assert narrative_is_faithful(narrative, facts) is True


def test_an_invented_amount_is_still_caught_with_legacy_ids() -> None:
    # The fence must not be one-sided: widening the tokenizer must never cost the guard
    # its actual job. A narrative citing an amount absent from the facts is unfaithful,
    # and stays unfaithful — before and after the ISO widening.
    facts = _facts(
        account=_LEGACY_ACCOUNT,
        transaction_id=_LEGACY_TXN_ID,
        counterparty="ACC-0023",
    )
    narrative = (
        f"A STRUCTURING pattern was detected on account {_LEGACY_ACCOUNT}. "
        f"Transaction {_LEGACY_TXN_ID} moved 45000.00 USD to ACC-0023."
    )
    assert narrative_is_faithful(narrative, facts) is False
