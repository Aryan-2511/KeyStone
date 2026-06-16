"""Validate the curated obligation graph's citation accuracy budget (KS-0205).

The loader (`keystone.core.obligations.load_obligations`) already fails loudly on
*structural* defects — missing fields, unknown enums, duplicate ids, citation /
node instrument drift (ADR-0012 decision 2). This validator adds the **accuracy
budget** on top: a missing or malformed source citation is a HARD build failure.

HARD, build-failing errors (per node):
  * the citation `provision` matches the per-instrument shape (e.g. EU AI Act /
    DORA are "Art. N"; DPDP Act is "s. N"; DPDP Rules are "Rule N"; RBI cites a
    named FREE-AI sutra; PMLA cites a section/rule of a named instrument);
  * `url`, when given, is an https link;
  * (plus every structural defect the loader already rejects: missing required
    citation fields, unknown enums, duplicate id, citation/node instrument drift.)

WARNINGS (surfaced, non-fatal):
  * `retrieved`, when given, is strictly after today (UTC). A provenance
    timestamp mildly ahead of the runner clock is not a citation-correctness
    defect — ADR-0012 treats `retrieved` as advisory — so it must not fail the
    build (that previously caused a timezone-dependent CI/local divergence).
    `retrieved` MAY be absent, and `retrieved == today` is valid.

`today` is computed as `datetime.now(timezone.utc).date()` (UTC-explicit) and is
injectable for deterministic, timezone-independent tests.

Run standalone (`python scripts/validate_obligations.py`), via `make verify`, or
through `tests/test_obligations.py`. Mirrors `scripts/validate_feature_list.py`:
`validate() -> list[str]` (errors) + `main() -> int`; `check()` also returns
warnings. Deterministic core only — no LLM, no network.
"""

from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

from keystone.core.obligations import Instrument, ObligationLoadError, load_obligations
from keystone.core.obligations.loader import DATA_PATH

# Per-instrument `provision` shape. The citation must locate a real provision of
# its instrument; free text or a wrong shape is a malformed citation (KS-0205).
_PROVISION_PATTERNS: dict[Instrument, re.Pattern[str]] = {
    # EU regulations cite an article, e.g. "Art. 9".
    Instrument.EU_AI_ACT: re.compile(r"^Art\. \d+$"),
    Instrument.DORA: re.compile(r"^Art\. \d+$"),
    # DPDP Act cites a section, e.g. "s. 8" or "s. 8(5)".
    Instrument.DPDP_ACT: re.compile(r"^s\. \d+(\(\w+\))?$"),
    # DPDP Rules 2025 cite a rule, e.g. "Rule 7".
    Instrument.DPDP_RULES_2025: re.compile(r"^Rule \d+$"),
    # RBI FREE-AI is advisory: cite a named sutra (by name, not number).
    Instrument.RBI_GUIDANCE: re.compile(r"^Sutra — \S.*$"),
    # PMLA/FIU-IND spans the Act + the 2005 Rules: "<locator>, <instrument>".
    Instrument.PMLA_FIU_IND: re.compile(r"^(s\. \d+|Rule \d+), \S.*$"),
}


def check(
    path: Path = DATA_PATH, today: datetime.date | None = None
) -> tuple[list[str], list[str]]:
    """Validate the obligation citations. Return ``(errors, warnings)``.

    ``errors`` are hard, build-failing defects; a non-empty list means the build
    should fail. ``warnings`` are surfaced but non-fatal. Structural load
    failures are surfaced as a single error rather than raised, so the caller
    treats them the same as accuracy-budget violations.

    ``today`` defaults to the current UTC date; it is injectable so the
    future-date check is deterministic regardless of the runner's timezone.
    """
    try:
        obligations = load_obligations(path)
    except ObligationLoadError as exc:
        return [f"obligation graph failed to load: {exc}"], []

    if today is None:
        today = datetime.datetime.now(datetime.UTC).date()

    errors: list[str] = []
    warnings: list[str] = []
    for obligation in obligations:
        citation = obligation.citation
        pattern = _PROVISION_PATTERNS[obligation.instrument]
        if not pattern.fullmatch(citation.provision):
            errors.append(
                f"{obligation.id}: provision {citation.provision!r} does not match "
                f"the {obligation.instrument} pattern {pattern.pattern!r}"
            )
        if citation.url is not None and not citation.url.startswith("https://"):
            errors.append(f"{obligation.id}: citation.url must be an https link")
        # Advisory provenance timestamp (ADR-0012): a date strictly after today
        # (UTC) is anomalous but not a correctness defect — warn, don't fail.
        if citation.retrieved is not None and citation.retrieved > today:
            warnings.append(
                f"{obligation.id}: citation.retrieved {citation.retrieved.isoformat()} "
                "is after today (UTC)"
            )

    return errors, warnings


def validate(path: Path = DATA_PATH, today: datetime.date | None = None) -> list[str]:
    """Hard, build-failing errors only — the gate `make verify` keys off."""
    return check(path, today)[0]


def main() -> int:
    """Print the validation outcome and return a process exit code."""
    errors, warnings = check()
    for warning in warnings:
        print(f"obligations.json: warning: {warning}", file=sys.stderr)
    if errors:
        print(f"obligations.json: {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("obligations.json: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
