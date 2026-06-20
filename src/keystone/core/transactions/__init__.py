"""Synthetic transaction substrate (deterministic core, Layer 1 — KS-0401).

Public surface: the `Transaction` model with its `Currency`/`TransactionType`
enums, and the seeded `generate_stream` / `sample_stream` generator (plus the
`StreamConfig` and the structuring-pattern constants). The data layer all of
Layer 1 operates on — no fraud detection (KS-0402), no seam (KS-0403) yet. No LLM
or network deps (ADR-0008).
"""

from __future__ import annotations

from .generator import (
    SAMPLE_STREAM_CONFIG,
    STRUCTURING_MIN_COUNT,
    STRUCTURING_THRESHOLD,
    StreamConfig,
    generate_stream,
    sample_stream,
    structuring_cluster,
)
from .models import Currency, Transaction, TransactionType

__all__ = [
    "SAMPLE_STREAM_CONFIG",
    "STRUCTURING_MIN_COUNT",
    "STRUCTURING_THRESHOLD",
    "Currency",
    "StreamConfig",
    "Transaction",
    "TransactionType",
    "generate_stream",
    "sample_stream",
    "structuring_cluster",
]
