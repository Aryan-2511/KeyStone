"""Shared control library + obligations crosswalk (deterministic core).

Public surface: the `Control` and `SpineMapping` models, the `Framework` enum,
the fail-loud `load_controls` loader and its `ControlLoadError`, the packaged
`DATA_PATH`, and the `build_crosswalk`/`ControlMapping` lookup. No LLM or network
deps (ADR-0008); Option A + the §5b invariant are locked by ADR-0012.
"""

from __future__ import annotations

from .crosswalk import ControlMapping, build_crosswalk
from .loader import DATA_PATH, ControlLoadError, load_controls
from .models import Control, Framework, SpineMapping

__all__ = [
    "DATA_PATH",
    "Control",
    "ControlLoadError",
    "ControlMapping",
    "Framework",
    "SpineMapping",
    "build_crosswalk",
    "load_controls",
]
