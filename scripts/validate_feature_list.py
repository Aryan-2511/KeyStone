"""Validate docs/feature_list.json — the machine-checkable feature primitive.

Fails (non-zero exit / non-empty error list) if the file is malformed or
references tests that don't exist. Run standalone (`python
scripts/validate_feature_list.py`), via `make verify`, or through
`tests/test_feature_list.py`.

Rules enforced (see the file's own "rules" block):
  * ids match KS-NNNN and are unique;
  * status is one of the declared status_values;
  * done_criteria is a non-empty list of strings for every item;
  * tests is non-empty once status passes 'planned';
  * every test ref "path" or "path::node" resolves to a real test file (and,
    if a node is given, a real test function/method in that file).
"""

from __future__ import annotations

import ast
import json
import re
import sys
from functools import cache
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
FEATURE_LIST = REPO_ROOT / "docs" / "feature_list.json"

ID_RE = re.compile(r"^KS-\d{4}$")
TERMINAL_STATUSES = {"in_progress", "done"}


@cache
def _collect_test_names(path: Path) -> frozenset[str]:
    """Return test function/method names defined in a test module via AST.

    Cached because several features reference the same file. Returns an empty
    set if the file cannot be parsed (the caller reports the missing file).
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return frozenset()

    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            names.add(node.name)
    return frozenset(names)


def _validate_test_ref(ref: str) -> str | None:
    """Return an error string for a bad test reference, else None."""
    file_part, _, node = ref.partition("::")
    test_file = REPO_ROOT / file_part
    if not test_file.is_file():
        return f"references missing test file {file_part!r}"
    if node and node not in _collect_test_names(test_file):
        return f"references missing test {node!r} in {file_part!r}"
    return None


def _validate_tests_field(tag: str, status: Any, tests: Any) -> list[str]:
    """Validate one feature's `tests` field against its status."""
    if not isinstance(tests, list):
        return [f"{tag}: tests must be a list"]

    errors: list[str] = []
    if status in TERMINAL_STATUSES and not tests:
        errors.append(f"{tag}: status {status!r} requires at least one test")

    for ref in tests:
        if not isinstance(ref, str):
            errors.append(f"{tag}: test ref {ref!r} must be a string")
            continue
        problem = _validate_test_ref(ref)
        if problem is not None:
            errors.append(f"{tag}: {problem}")
    return errors


def _validate_feature(feat: dict[str, Any], status_values: set[str]) -> list[str]:
    """Validate a single feature object (excluding cross-item id uniqueness)."""
    tag = feat.get("id", "<no-id>")
    errors: list[str] = []

    if not ID_RE.match(feat.get("id", "")):
        errors.append(f"{tag}: id must match KS-NNNN")

    status = feat.get("status")
    if status not in status_values:
        errors.append(f"{tag}: status {status!r} not in {sorted(status_values)}")

    criteria = feat.get("done_criteria")
    if not isinstance(criteria, list) or not criteria:
        errors.append(f"{tag}: done_criteria must be a non-empty list")
    elif not all(isinstance(c, str) and c.strip() for c in criteria):
        errors.append(f"{tag}: done_criteria entries must be non-empty strings")

    errors.extend(_validate_tests_field(tag, status, feat.get("tests")))
    return errors


def validate(path: Path = FEATURE_LIST) -> list[str]:
    """Validate the feature list. Return a list of human-readable errors."""
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"{path} not found"]
    except json.JSONDecodeError as exc:
        return [f"{path} is not valid JSON: {exc}"]

    errors: list[str] = []
    status_values = set(data.get("status_values", []))
    if not status_values:
        errors.append("top-level 'status_values' is missing or empty")

    features = data.get("features")
    if not isinstance(features, list) or not features:
        return [*errors, "top-level 'features' must be a non-empty list"]

    seen_ids: set[str] = set()
    for feat in features:
        fid = feat.get("id", "")
        if fid in seen_ids:
            errors.append(f"{fid or '<no-id>'}: duplicate id")
        seen_ids.add(fid)
        errors.extend(_validate_feature(feat, status_values))

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print(f"feature_list.json: {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("feature_list.json: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
