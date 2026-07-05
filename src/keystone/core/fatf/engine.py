"""Deterministic FATF typology detection engine (KS-0402, Layer 1).

Deterministic core (ADR-0008): no LLM, no network. Detects financial-crime
patterns in a stream of `Transaction`s using FINANCIAL SIGNALS ONLY and records
findings to the evidence ledger.

MEMO-BLINDNESS (thesis-critical): NOTHING here reads `Transaction.memo`. Detection
keys on amounts, timing/velocity, account relationships, and thresholds. This
orthogonality is what makes the KS-0403 seam honest — the seam fraud is caught
here for AML reasons AND (separately) carries an injection the assurance loop
flags. If detection ever depended on memo content, "same gap, two independent
detections" would be circular. A test pins this invariant.

Typologies (each a deterministic rule with NAMED, configurable thresholds):
- STRUCTURING / smurfing — many sub-threshold transfers from one account in a
  window (deliberately under the CTR reporting threshold);
- RAPID_MOVEMENT / velocity — a burst of transfers from one account in a tight
  window (fan-out);
- LARGE_TRANSFER — a single transfer at/over the CTR reporting threshold.
"""

from __future__ import annotations

import datetime
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass

from keystone.core.ledger import Ledger, LedgerEntry, open_ledger
from keystone.core.transactions import Transaction, TransactionType

from .models import Finding, Severity, Typology

LEDGER_AGENT = "fatf-monitor"
LEDGER_LAYER = "L1"
LEDGER_ACTION = "fatf_finding"

# A STANDING flagged-destination list (KS-0605) — sanctions-style recipient screening.
# This is fixed core data that exists INDEPENDENTLY of any attack: the screen flags a
# payment because its destination is on this list, exactly as a real sanctions screen
# would, never because some attack named the recipient. Synthetic, minimal (a small
# fixed set in a dedicated ACC-9xxx range, disjoint from the normal account pool) — NOT
# a real feed, NOT fuzzy matching, NOT entity resolution. Just membership.
FLAGGED_DESTINATIONS: frozenset[str] = frozenset({"ACC-9001", "ACC-9002", "ACC-9003"})


@dataclass(frozen=True)
class FatfThresholds:
    """Named, configurable FATF thresholds (no magic numbers in the rules)."""

    # Currency Transaction Report threshold; single transfers >= this are reportable.
    ctr_threshold: float = 10_000.0
    # Transfers in [band_floor, ctr) are "sub-threshold" (structuring band).
    structuring_band_floor: float = 5_000.0
    # A structuring cluster needs at least this many sub-threshold transfers...
    structuring_min_transfers: int = 3
    # ...within this window.
    structuring_window: datetime.timedelta = datetime.timedelta(hours=24)
    # Rapid movement: this many transfers from one account...
    rapid_min_transfers: int = 5
    # ...within this tight window.
    rapid_window: datetime.timedelta = datetime.timedelta(hours=1)


DEFAULT_THRESHOLDS = FatfThresholds()

# An ENHANCED-SCRUTINY profile (MC-PRE-01): the same memo-blind rules run at tightened
# thresholds — the financial-side remediation (c). It halves the CTR reporting threshold
# (10k → 5k) so a LONE transfer deliberately sized just under the standard 10k threshold —
# an evasion the baseline lets pass (it is neither a ≥3 structuring cluster nor a ≥10k
# large transfer) — is now a reportable LARGE_TRANSFER; the structuring band floor is
# lowered in step (5k → 2.5k) so the band stays valid and smaller smurfing is caught too.
# It is a stricter PROFILE, not a logic change: `detect` already takes the thresholds as a
# parameter (memo-blind either way). `DEFAULT_THRESHOLDS` and baseline behaviour are
# unchanged. Applied as remediation (c) via `keystone.assurance.remediation`.
STRICT_THRESHOLDS = FatfThresholds(
    ctr_threshold=5_000.0,
    structuring_band_floor=2_500.0,
)


def _transfers_by_sender(
    transactions: Sequence[Transaction],
) -> dict[str, list[Transaction]]:
    """Group TRANSFERs by sender, each list sorted by (timestamp, id). Memo-blind."""
    buckets: dict[str, list[Transaction]] = defaultdict(list)
    for txn in transactions:
        if txn.tx_type is TransactionType.TRANSFER:
            buckets[txn.sender_account].append(txn)
    for group in buckets.values():
        group.sort(key=lambda t: (t.timestamp, t.id))
    return buckets


def _densest_window(
    txns: list[Transaction], window: datetime.timedelta, min_count: int
) -> list[Transaction] | None:
    """Return the largest set of `txns` (time-sorted) within `window`, or None.

    Two-pointer sweep: for each left edge, extend right while inside the window;
    keep the widest qualifying span. Deterministic — no memo read.
    """
    best: list[Transaction] = []
    left = 0
    for right in range(len(txns)):
        while txns[right].timestamp - txns[left].timestamp > window:
            left += 1
        span = txns[left : right + 1]
        if len(span) >= min_count and len(span) > len(best):
            best = span
    return best or None


def _detect_structuring(
    transactions: Sequence[Transaction], th: FatfThresholds
) -> list[Finding]:
    findings: list[Finding] = []
    by_sender = _transfers_by_sender(transactions)
    for sender, group in sorted(by_sender.items()):
        sub = [
            t for t in group if th.structuring_band_floor <= t.amount < th.ctr_threshold
        ]
        cluster = _densest_window(
            sub, th.structuring_window, th.structuring_min_transfers
        )
        if cluster is None:
            continue
        total = round(sum(t.amount for t in cluster), 2)
        minutes = (cluster[-1].timestamp - cluster[0].timestamp).total_seconds() / 60
        findings.append(
            Finding(
                typology=Typology.STRUCTURING,
                severity=Severity.HIGH,
                account=sender,
                transaction_ids=tuple(t.id for t in cluster),
                signal={
                    "transfer_count": len(cluster),
                    "total_amount": total,
                    "window_minutes": round(minutes, 1),
                    "amount_band": [th.structuring_band_floor, th.ctr_threshold],
                },
                rationale=(
                    f"{len(cluster)} transfers totalling {total} from {sender}, each "
                    f"between {th.structuring_band_floor:.0f} and {th.ctr_threshold:.0f} "
                    f"(just under the CTR threshold) within {round(minutes)} minutes — "
                    "structuring / smurfing to avoid the reporting threshold."
                ),
            )
        )
    return findings


def _detect_rapid_movement(
    transactions: Sequence[Transaction], th: FatfThresholds
) -> list[Finding]:
    findings: list[Finding] = []
    by_sender = _transfers_by_sender(transactions)
    for sender, group in sorted(by_sender.items()):
        burst = _densest_window(group, th.rapid_window, th.rapid_min_transfers)
        if burst is None:
            continue
        recipients = sorted({t.recipient_account for t in burst})
        minutes = (burst[-1].timestamp - burst[0].timestamp).total_seconds() / 60
        findings.append(
            Finding(
                typology=Typology.RAPID_MOVEMENT,
                severity=Severity.MEDIUM,
                account=sender,
                transaction_ids=tuple(t.id for t in burst),
                signal={
                    "transfer_count": len(burst),
                    "recipient_count": len(recipients),
                    "window_minutes": round(minutes, 1),
                },
                rationale=(
                    f"{len(burst)} transfers from {sender} to {len(recipients)} "
                    f"recipients within {round(minutes)} minutes — rapid movement / "
                    "fan-out (layering)."
                ),
            )
        )
    return findings


def _detect_large_transfer(
    transactions: Sequence[Transaction], th: FatfThresholds
) -> list[Finding]:
    findings: list[Finding] = []
    for txn in transactions:
        if txn.tx_type is TransactionType.TRANSFER and txn.amount >= th.ctr_threshold:
            findings.append(
                Finding(
                    typology=Typology.LARGE_TRANSFER,
                    severity=Severity.HIGH,
                    account=txn.sender_account,
                    transaction_ids=(txn.id,),
                    signal={"amount": txn.amount, "ctr_threshold": th.ctr_threshold},
                    rationale=(
                        f"Transfer of {txn.amount} from {txn.sender_account} at or "
                        f"over the {th.ctr_threshold:.0f} CTR reporting threshold."
                    ),
                )
            )
    return findings


def _detect_unauthorized_recipient(
    transactions: Sequence[Transaction],
    flagged: frozenset[str] = FLAGGED_DESTINATIONS,
) -> list[Finding]:
    """Flag transfers whose DESTINATION is on the standing flagged-destination list.

    Memo-blind: reads the recipient account (a financial signal) and checks membership
    of the STANDING `flagged` list — never any attack channel, never why the payment was
    made. Sanctions-style screening: a new SIGNAL TYPE (list membership) distinct from
    the intrinsic-pattern typologies above.
    """
    findings: list[Finding] = []
    for txn in transactions:
        if txn.tx_type is TransactionType.TRANSFER and txn.recipient_account in flagged:
            findings.append(
                Finding(
                    typology=Typology.UNAUTHORIZED_RECIPIENT,
                    severity=Severity.HIGH,
                    account=txn.sender_account,
                    transaction_ids=(txn.id,),
                    signal={
                        "recipient_account": txn.recipient_account,
                        "amount": txn.amount,
                        "flagged_list_size": len(flagged),
                    },
                    rationale=(
                        f"Transfer from {txn.sender_account} to "
                        f"{txn.recipient_account}, which is on the standing "
                        "flagged-destination (sanctions-style) screening list — "
                        "unauthorized / prohibited recipient."
                    ),
                )
            )
    return findings


def detect(
    transactions: Sequence[Transaction], thresholds: FatfThresholds = DEFAULT_THRESHOLDS
) -> list[Finding]:
    """Run all FATF typology rules over `transactions`. Memo-blind, deterministic.

    Findings are returned ordered by typology then account for reproducibility.
    """
    findings = [
        *_detect_structuring(transactions, thresholds),
        *_detect_rapid_movement(transactions, thresholds),
        *_detect_large_transfer(transactions, thresholds),
        *_detect_unauthorized_recipient(transactions),
    ]
    return sorted(findings, key=lambda f: (f.typology.value, f.account))


def record_findings(
    findings: Sequence[Finding], *, ledger: Ledger | None = None
) -> list[LedgerEntry]:
    """Write FATF findings to the evidence ledger (auditable, hash-chained)."""
    led = ledger if ledger is not None else open_ledger()
    return [
        led.append(
            agent=LEDGER_AGENT,
            layer=LEDGER_LAYER,
            action=LEDGER_ACTION,
            payload={
                "typology": finding.typology.value,
                "severity": finding.severity.value,
                "account": finding.account,
                "transaction_ids": list(finding.transaction_ids),
                "signal": finding.signal,
                "rationale": finding.rationale,
            },
        )
        for finding in findings
    ]
