"""Smoke test: the package imports and advertises a version.

This exists so the test gate has something to run during Phase 0. No
application logic is exercised here.
"""

import pytest

import keystone
from keystone.__main__ import main


def test_package_imports() -> None:
    assert keystone is not None


def test_version_is_set() -> None:
    assert isinstance(keystone.__version__, str)
    assert keystone.__version__


def test_main_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    out = capsys.readouterr().out
    assert keystone.__version__ in out
