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


def _run_demo(*, live: bool = False) -> int:
    """Run the real arc and narrate the genuine RunResult it produced.

    Offline by default (no Ollama, no Garak, no network). With `live`, the two AGENTS go
    live, each with its own fallback: the Red-Team Agent runs its full policy-selected
    sequence as REAL Garak scans (OPT-A-02; slow — minutes), and the Triage Agent reasons
    the route with a local LLM (OPT-A-01). The rest of the arc stays offline; the
    narration states, per agent, what actually ran (real scan vs recorded, LLM vs policy).
    """
    result = build_run_result(live=live)
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
    demo_parser = sub.add_parser(
        "demo",
        help="run the real assurance arc offline and narrate its result (default)",
    )
    demo_parser.add_argument(
        "--live",
        action="store_true",
        help=(
            "take the two agents live: the Red-Team Agent runs REAL Garak scans of its "
            "full selected sequence (slow, minutes; falls back to the recorded profile) "
            "and the Triage Agent LLM-reasons the route (falls back to the policy). "
            "Opt-in; the rest of the arc stays offline. Without this flag the front door "
            "is fully offline and needs no Garak/Ollama."
        ),
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
        return _run_demo(live=bool(getattr(args, "live", False)))
    except Exception as exc:  # fail-loud: clear message + non-zero exit
        print(f"keystone demo failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
