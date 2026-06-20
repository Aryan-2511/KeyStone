"""Live wiring for the assurance loop (KS-0304).

Kept separate from `loop.py` so the loop SPINE (and its fast tests) stay free of
nemoguardrails and the live backends — importing this module is what pulls them
in, only for the NAT-orchestrated milestone run. Each dep is one existing
component (KS-0301 agent, KS-0303 Garak scans, KS-0302 guarded agent); no new
capability.
"""

from __future__ import annotations

from keystone.core.ledger import Ledger
from keystone.llm.inference import OllamaBackend

from .agent import Transaction, run_agent
from .garak_endpoint import scan_guarded_agent
from .garak_probe import parse_report, scan_mock_agent
from .guard import run_guarded_agent
from .loop import LoopDeps
from .signature import CANONICAL_MEMO_EXPLOIT


def live_deps(*, ledger: Ledger, prompt_cap: int = 12) -> LoopDeps:
    """Wire the real KS-0301/0303/0302 components as the loop's four stages."""

    def _exploit_txn() -> Transaction:
        return Transaction(
            amount=200.0, sender="Bob Smith", memo=CANONICAL_MEMO_EXPLOIT.memo
        )

    return LoopDeps(
        expose=lambda: run_agent(
            _exploit_txn(), backend=OllamaBackend(), ledger=ledger
        ),
        detect=lambda: parse_report(
            scan_mock_agent(report_prefix="ks0304_detect", prompt_cap=prompt_cap)
        ),
        rescan=lambda: parse_report(
            scan_guarded_agent(report_prefix="ks0304_verify", prompt_cap=prompt_cap)
        ),
        reverify=lambda: run_guarded_agent(
            _exploit_txn(), backend=OllamaBackend(), ledger=ledger
        ),
    )
