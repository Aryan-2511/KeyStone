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
from keystone.demo.runner import OFFLINE_MODES, LiveModes


def _use_utf8_stdout() -> None:
    """Render UTF-8 on any console (e.g. Windows cp1252) so real field text — which
    may contain non-ASCII — never crashes the front door. A no-op when stdout is not
    a real text stream (e.g. under pytest's output capture)."""
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")


def _run_demo(*, live: LiveModes = OFFLINE_MODES) -> int:
    """Run the real arc and narrate the genuine RunResult it produced.

    Offline by default (no Ollama, no Garak, no network). `live` (OPT-A-02b) controls the
    two agents' live modes INDEPENDENTLY: live triage LLM-reasons the route (OPT-A-01),
    live red-team runs REAL Garak scans (OPT-A-02) bounded to the TRACTABLE probe set
    unless `live.deep`. The rest of the arc stays offline; the narration states, per agent,
    what actually ran (real scan vs recorded, which scope, LLM vs policy).
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
            "take BOTH agents live: the Triage Agent LLM-reasons the route (OPT-A-01) and "
            "the Red-Team Agent runs REAL Garak scans of the TRACTABLE probe set (minutes, "
            "not hours; add --deep for the full set). Each falls back on failure. Opt-in; "
            "the rest of the arc stays offline. Equivalent to --live-triage --live-redteam."
        ),
    )
    demo_parser.add_argument(
        "--live-triage",
        action="store_true",
        help=(
            "take ONLY the Triage Agent live (qwen2.5:3b via Ollama; falls back to the "
            "policy). The Red-Team Agent stays on the recorded profile — no Garak scan, "
            "so live triage never triggers the hours-long red-team scan."
        ),
    )
    demo_parser.add_argument(
        "--live-redteam",
        action="store_true",
        help=(
            "take ONLY the Red-Team Agent live: REAL Garak scans of the TRACTABLE probe "
            "set by default (minutes; add --deep for the full set incl. the intractable "
            "deep probes). Falls back to the recorded profile. Triage stays on the policy."
        ),
    )
    demo_parser.add_argument(
        "--deep",
        action="store_true",
        help=(
            "with a live red-team, scan the FULL probe set incl. the known-intractable "
            "deep probes (LatentWhois ~1550s, the *Full variants ~955s+; the whole "
            "sequence can take HOURS). Implies --live-redteam. Default live is tractable."
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

    # command == "demo". Resolve the granular live flags (OPT-A-02b): --live means both
    # agents live; --deep implies a live red-team (you asked for the deep scan).
    both = bool(getattr(args, "live", False))
    deep = bool(getattr(args, "deep", False))
    live = LiveModes(
        triage=bool(getattr(args, "live_triage", False)) or both,
        redteam=bool(getattr(args, "live_redteam", False)) or both or deep,
        deep=deep,
    )
    try:
        return _run_demo(live=live)
    except Exception as exc:  # fail-loud: clear message + non-zero exit
        print(f"keystone demo failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
