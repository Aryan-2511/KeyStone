"""Deterministic synthetic transaction generator (KS-0401, Layer 1).

Deterministic core (ADR-0008): no LLM, no network, no real PII. A seeded generator
produces a reproducible stream of mostly-normal transactions, with the explicit,
opt-in ability to seed FATF-detectable patterns — specifically a STRUCTURING /
RAPID-MOVEMENT cluster (many transfers from one account, each just under a
reporting threshold, minutes apart). Patterns are produced by EXPLICIT config, not
random surprise.

The generator labels NOTHING as fraud — it just produces data; identifying the
cluster is KS-0402's typology engine. The point of KS-0401 is only that the
substrate CAN express independently-suspicious financial behaviour (and carry an
arbitrary memo) so the later seam (KS-0403) is possible.
"""

from __future__ import annotations

import datetime
import random
from dataclasses import dataclass

from .models import Currency, Transaction, TransactionType

# A synthetic reporting threshold; structuring transfers sit JUST under it.
STRUCTURING_THRESHOLD = 10_000.0
# Minimum transfers for a structuring cluster (FATF smurfing pattern).
STRUCTURING_MIN_COUNT = 6

# Fixed epoch so streams are reproducible (never `datetime.now`).
_EPOCH = datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC)

# Benign free-text memos for normal traffic (no instructions; untrusted-data field).
_BENIGN_MEMOS = (
    "Invoice payment",
    "Monthly subscription",
    "Salary",
    "Refund",
    "Consulting services",
    "Utility bill",
    "Rent",
    "",
)


@dataclass(frozen=True)
class StreamConfig:
    """Seeded configuration for a reproducible synthetic stream."""

    seed: int = 42
    normal_count: int = 40
    account_pool: int = 25
    structuring_clusters: int = 0
    currency: Currency = Currency.USD
    start: datetime.datetime = _EPOCH


def _accounts(config: StreamConfig) -> list[str]:
    return [f"ACC-{i:04d}" for i in range(1, config.account_pool + 1)]


@dataclass
class _Raw:
    """Pre-id transaction data, gathered then sorted + numbered into Transactions."""

    timestamp: datetime.datetime
    sender: str
    recipient: str
    amount: float
    tx_type: TransactionType
    memo: str = ""


def _normal(
    rng: random.Random, accounts: list[str], start: datetime.datetime, n: int
) -> list[_Raw]:
    rows: list[_Raw] = []
    clock = start
    for _ in range(n):
        clock += datetime.timedelta(minutes=rng.randint(5, 180))
        sender, recipient = rng.sample(accounts, 2)
        rows.append(
            _Raw(
                timestamp=clock,
                sender=sender,
                recipient=recipient,
                amount=round(rng.uniform(20.0, 3000.0), 2),
                tx_type=rng.choice(list(TransactionType)),
                memo=rng.choice(_BENIGN_MEMOS),
            )
        )
    return rows


def structuring_cluster(
    rng: random.Random, accounts: list[str], start: datetime.datetime
) -> list[_Raw]:
    """One structuring / rapid-movement cluster (FATF smurfing).

    A single sender pushes many transfers, each JUST under `STRUCTURING_THRESHOLD`,
    to a few recipients within minutes — independently suspicious on financial-crime
    grounds, with no memo content required.
    """
    sender = rng.choice(accounts)
    pool = [a for a in accounts if a != sender]
    recipients = rng.sample(pool, k=min(3, len(pool)))
    count = rng.randint(STRUCTURING_MIN_COUNT, STRUCTURING_MIN_COUNT + 3)

    rows: list[_Raw] = []
    clock = start
    for _ in range(count):
        clock += datetime.timedelta(minutes=rng.randint(2, 15))
        rows.append(
            _Raw(
                timestamp=clock,
                sender=sender,
                recipient=rng.choice(recipients),
                amount=round(
                    rng.uniform(
                        STRUCTURING_THRESHOLD * 0.90, STRUCTURING_THRESHOLD * 0.99
                    ),
                    2,
                ),
                tx_type=TransactionType.TRANSFER,
                memo=rng.choice(_BENIGN_MEMOS),
            )
        )
    return rows


def generate_stream(config: StreamConfig | None = None) -> list[Transaction]:
    """Generate a reproducible stream: same config → byte-identical Transactions.

    Produces `normal_count` ordinary transactions plus `structuring_clusters`
    seeded structuring clusters, then orders by timestamp and assigns stable ids.
    """
    cfg = config or StreamConfig()
    # Synthetic data MUST be seed-reproducible (a CSPRNG can't be); not security.
    rng = random.Random(cfg.seed)  # noqa: S311
    accounts = _accounts(cfg)

    rows = _normal(rng, accounts, cfg.start, cfg.normal_count)
    for index in range(cfg.structuring_clusters):
        cluster_start = cfg.start + datetime.timedelta(days=1 + index)
        rows += structuring_cluster(rng, accounts, cluster_start)

    rows.sort(key=lambda r: (r.timestamp, r.sender, r.recipient))
    return [
        Transaction(
            id=f"TXN-{i:06d}",
            timestamp=row.timestamp,
            sender_account=row.sender,
            recipient_account=row.recipient,
            amount=row.amount,
            currency=cfg.currency,
            tx_type=row.tx_type,
            memo=row.memo,
        )
        for i, row in enumerate(rows, start=1)
    ]


# The canonical fixture the rest of Layer 1 builds on: normal traffic + one
# structuring cluster, fully reproducible.
SAMPLE_STREAM_CONFIG = StreamConfig(
    seed=20260101, normal_count=30, structuring_clusters=1
)


def sample_stream() -> list[Transaction]:
    """The deterministic Layer-1 sample stream (normal + one structuring cluster)."""
    return generate_stream(SAMPLE_STREAM_CONFIG)


__all__ = [
    "SAMPLE_STREAM_CONFIG",
    "STRUCTURING_MIN_COUNT",
    "STRUCTURING_THRESHOLD",
    "StreamConfig",
    "generate_stream",
    "sample_stream",
    "structuring_cluster",
]
