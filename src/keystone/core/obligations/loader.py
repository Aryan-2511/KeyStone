"""Fail-loud loader for the curated obligation graph (ADR-0012 #2).

A malformed node, an unknown enum value, a missing required citation field, or a
duplicate `id` is a HARD error: obligations are never skipped, defaulted, or
partially loaded. A silently-dropped obligation is exactly the coverage gap this
product exists to catch. Deterministic core: no LLM, no network.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .models import Obligation

# Curated data ships as package data (ADR-0012 #1), mirroring workflow.yml.
DATA_PATH = Path(__file__).parent / "data" / "obligations.json"


class ObligationLoadError(Exception):
    """Raised when the obligation data file is malformed or inconsistent."""


def load_obligations(path: Path | None = None) -> list[Obligation]:
    """Load and validate the obligation graph, or raise `ObligationLoadError`.

    Validates every node against the locked schema and rejects duplicate ids.
    There is no partial-success path: any defect fails the whole load.
    """
    data_path = path or DATA_PATH
    try:
        raw = json.loads(data_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ObligationLoadError(
            f"obligation data file not found: {data_path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ObligationLoadError(
            f"obligation data file is not valid JSON: {exc}"
        ) from exc

    if not isinstance(raw, list):
        raise ObligationLoadError(
            "obligation data file must be a JSON array of objects"
        )

    obligations: list[Obligation] = []
    seen: set[str] = set()
    for index, node in enumerate(raw):
        try:
            obligation = Obligation.model_validate(node)
        except ValidationError as exc:
            raise ObligationLoadError(
                f"obligation at index {index} is invalid: {exc}"
            ) from exc
        if obligation.id in seen:
            raise ObligationLoadError(f"duplicate obligation id: {obligation.id!r}")
        seen.add(obligation.id)
        obligations.append(obligation)

    return obligations
