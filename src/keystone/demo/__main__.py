"""`python -m keystone.demo` — build the golden-path run-result and save it.

Runs one Layer-1 arc offline (deterministic template narrative — no network) and
writes the typed run-result to `KEYSTONE_RUN_JSON` (default `keystone-run.json`),
the saved run the Phase-5 screens replay. Pass a path to override.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence

from .runner import build_run_result, run_json_path, save_run_result


def main_with_args(argv: Sequence[str]) -> None:
    """Build + save a run-result; `argv` is the optional [path] override."""
    path = argv[0] if argv else run_json_path()
    result = build_run_result()
    written = save_run_result(result, path)
    print(f"run-result written: {written}")
    print(
        f"seam tx: {result.binding.transaction_id}  "
        f"signature: {result.binding.signature_name}  "
        f"typology: {result.binding.fatf_typology}"
    )
    print(
        f"arc: {' -> '.join(result.arc.stages)}  "
        f"chain_ok: {result.arc.chain_verified}  "
        f"entries: {result.arc.entry_count}"
    )


def main() -> None:
    main_with_args(sys.argv[1:])


if __name__ == "__main__":
    main()
