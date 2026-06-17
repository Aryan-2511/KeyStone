"""Fail-loud loader for the shared control library (ADR-0012 §5).

A malformed control, an unknown enum value, a missing required field, or a
duplicate `id` is a HARD error: controls are never skipped, defaulted, or
partially loaded — the same invariant as the obligation loader. Deterministic
core: no LLM, no network.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .models import Control

# Curated data ships as package data (ADR-0012), mirroring the obligation graph.
DATA_PATH = Path(__file__).parent / "data" / "controls.json"


class ControlLoadError(Exception):
    """Raised when the control data file is malformed or inconsistent."""


def load_controls(path: Path | None = None) -> list[Control]:
    """Load and validate the control library, or raise `ControlLoadError`.

    Validates every control against the locked schema and rejects duplicate ids.
    There is no partial-success path: any defect fails the whole load.
    """
    data_path = path or DATA_PATH
    try:
        raw = json.loads(data_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ControlLoadError(f"control data file not found: {data_path}") from exc
    except json.JSONDecodeError as exc:
        raise ControlLoadError(f"control data file is not valid JSON: {exc}") from exc

    if not isinstance(raw, list):
        raise ControlLoadError("control data file must be a JSON array of objects")

    controls: list[Control] = []
    seen: set[str] = set()
    for index, node in enumerate(raw):
        try:
            control = Control.model_validate(node)
        except ValidationError as exc:
            raise ControlLoadError(
                f"control at index {index} is invalid: {exc}"
            ) from exc
        if control.id in seen:
            raise ControlLoadError(f"duplicate control id: {control.id!r}")
        seen.add(control.id)
        controls.append(control)

    return controls
