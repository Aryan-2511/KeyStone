"""The `keystone` console entry point — the project's front door.

`keystone demo` (the default) runs the real Layer-1 assurance arc once, **offline
and deterministic** (no Ollama, no Garak, no network), and narrates the actual
`RunResult` it produced: the FATF finding, the Red-Team Agent's landed exploit, the
seam bind, the Triage Agent's route, and the sealed hash-chained ledger. It is the
same genuine arc `make demo` and the Streamlit UI render — one real path, reached
three ways.

Fail-loud: exit 0 on success, non-zero (with a clear stderr message) on failure.
"""

from __future__ import annotations

import argparse
import io
import sys
from collections.abc import Sequence

from keystone import __version__
from keystone.demo import build_run_result
from keystone.demo.narrate import narrate_run


def _use_utf8_stdout() -> None:
    """Render UTF-8 on any console (e.g. Windows cp1252) so real field text — which
    may contain non-ASCII — never crashes the front door. A no-op when stdout is not
    a real text stream (e.g. under pytest's output capture)."""
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")


def _run_demo() -> int:
    """Run the real arc offline and narrate the genuine RunResult it produced."""
    result = build_run_result()  # offline default: template narrative, no network
    print(narrate_run(result))
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="keystone",
        description=(
            "Keystone — orchestrated compliance & assurance. "
            "Run `keystone demo` to see the real arc end to end (offline)."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"keystone {__version__}"
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser(
        "demo",
        help="run the real assurance arc offline and narrate its result (default)",
    )
    sub.add_parser("version", help="print the version and exit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Defaults to `demo` when no subcommand is given."""
    _use_utf8_stdout()
    parser = _build_parser()
    args = parser.parse_args(argv)
    command = args.command or "demo"

    if command == "version":
        print(f"keystone {__version__}")
        return 0

    # command == "demo"
    try:
        return _run_demo()
    except Exception as exc:  # fail-loud: clear message + non-zero exit
        print(f"keystone demo failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
