"""The feature primitive must be valid and self-consistent.

`scripts/validate_feature_list.py` is the single source of validation logic;
this test runs it (so a malformed feature_list.json fails CI's `check` gate as
well as `make verify`).
"""

from validate_feature_list import validate


def test_feature_list_is_valid() -> None:
    errors = validate()
    assert errors == [], "feature_list.json has errors:\n" + "\n".join(errors)
