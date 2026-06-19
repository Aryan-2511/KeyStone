"""The feature primitive must be valid and self-consistent.

`scripts/validate_feature_list.py` is the single source of validation logic;
this test runs it (so a malformed feature_list.json fails CI's `check` gate as
well as `make verify`).
"""

from validate_feature_list import _validate_depends_on, validate


def test_feature_list_is_valid() -> None:
    errors = validate()
    assert errors == [], "feature_list.json has errors:\n" + "\n".join(errors)


def test_depends_on_accepts_existing_ids() -> None:
    assert _validate_depends_on("KS-0301", ["KS-0300"], {"KS-0300", "KS-0301"}) == []


def test_depends_on_rejects_unknown_id() -> None:
    errors = _validate_depends_on("KS-0301", ["KS-9999"], {"KS-0300", "KS-0301"})
    assert errors and "unknown feature" in errors[0]


def test_depends_on_rejects_self_reference() -> None:
    errors = _validate_depends_on("KS-0301", ["KS-0301"], {"KS-0301"})
    assert errors and "itself" in errors[0]


def test_depends_on_rejects_non_list() -> None:
    errors = _validate_depends_on("KS-0301", "KS-0300", {"KS-0300"})
    assert errors and "must be a list" in errors[0]
