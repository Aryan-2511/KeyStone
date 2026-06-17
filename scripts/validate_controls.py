"""Validate the obligations→controls crosswalk's referential integrity (KS-0202).

This is the §5b validator ADR-0012 owed to KS-0202, and the sibling of
`scripts/validate_obligations.py`. The control and obligation loaders already
fail loud on *structural* defects; this validator enforces the crosswalk
invariants that make the control library trustworthy as a HARD build failure:

  * §5b referential integrity — every non-empty `control_id` on every obligation
    MUST resolve to a real control in the library; an unresolved reference is a
    hard error (never skipped, never defaulted);
  * coverage — every obligation maps to at least one control (KS-0202 populates
    the references ADR-0012 §5a left optional);
  * no orphan control — every control is referenced by at least one obligation,
    so the library carries no dead controls.

Run standalone (`python scripts/validate_controls.py`), via `make verify`, or
through `tests/test_controls.py`. Mirrors the citation gate: `validate() ->
list[str]` + `main() -> int`. Deterministic core only — no LLM, no network.
"""

from __future__ import annotations

import sys
from pathlib import Path

from keystone.core.controls import ControlLoadError, load_controls
from keystone.core.obligations import ObligationLoadError, load_obligations


def validate(
    controls_path: Path | None = None, obligations_path: Path | None = None
) -> list[str]:
    """Validate the crosswalk. Return a list of human-readable errors.

    A non-empty list means the build should fail. Load failures are surfaced as
    error entries rather than raised, so the caller treats a malformed file the
    same as a referential-integrity violation.
    """
    try:
        controls = load_controls(controls_path)
    except ControlLoadError as exc:
        return [f"control library failed to load: {exc}"]
    try:
        obligations = load_obligations(obligations_path)
    except ObligationLoadError as exc:
        return [f"obligation graph failed to load: {exc}"]

    known_ids = {c.id for c in controls}
    referenced: set[str] = set()
    errors: list[str] = []

    for obligation in obligations:
        if not obligation.control_ids:
            errors.append(f"{obligation.id}: maps to no control (coverage gap)")
        for control_id in obligation.control_ids:
            if control_id not in known_ids:
                errors.append(
                    f"{obligation.id}: control_id {control_id!r} does not resolve "
                    "to a known control"
                )
            else:
                referenced.add(control_id)

    for control in controls:
        if control.id not in referenced:
            errors.append(f"{control.id}: orphan control — referenced by no obligation")

    return errors


def main() -> int:
    """Print the validation outcome and return a process exit code."""
    errors = validate()
    if errors:
        print(f"controls crosswalk: {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("controls crosswalk: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
