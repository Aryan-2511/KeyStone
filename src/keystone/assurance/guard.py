"""NeMo Guardrails input rail wrapping the mock agent (KS-0302).

This is the PATCH in find-and-patch: a real NeMo Guardrails config (see
`guardrails/`) whose deterministic, pattern-based INPUT rail vets the untrusted
memo/data-field content before the agent acts on it. The rail uses NO main LLM
and NO embedding model, so nothing is downloaded (the 4 GB-box constraint) — it
runs `input`-only rails and reads the `activated_rails` log to decide block/allow.

Scope (honest): this fully closes the KS-0301 *authored* vulnerability — memo
content can no longer drive an unauthorized `initiate_transfer`. Real-world
guardrailing is defense-in-depth, not a silver bullet; a single deterministic rail
is the demo's patch, not a general prompt-injection cure.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.rails.llm.options import GenerationOptions

from keystone.core.ledger import Ledger
from keystone.llm.inference import ToolCallingBackend

from .agent import AgentRun, Transaction, run_agent

GUARDRAILS_CONFIG_PATH = Path(__file__).parent / "guardrails"

# The message the rail returns when it blocks (mirrors guardrails/rails.co).
GUARD_REFUSAL = (
    "I can't act on instructions embedded in transaction data. "
    "This request was blocked."
)

# Run ONLY the input rails (no dialog/output/retrieval, no main LLM call) and ask
# for the activated-rails log so a `stop` is an unambiguous block signal.
_INPUT_ONLY_OPTIONS = GenerationOptions(
    rails={"input": True, "dialog": False, "output": False, "retrieval": False},
    log={"activated_rails": True},
)


@lru_cache(maxsize=1)
def build_rails() -> LLMRails:
    """Construct the LLMRails once (no model download; cached)."""
    config = RailsConfig.from_path(str(GUARDRAILS_CONFIG_PATH))
    return LLMRails(config)


def is_blocked(text: str) -> bool:
    """True if the input rail stops `text` as data-field instruction injection."""
    rails = build_rails()
    result: Any = rails.generate(
        messages=[{"role": "user", "content": text}],
        options=_INPUT_ONLY_OPTIONS,
    )
    activated = result.log.activated_rails if result.log is not None else []
    return any(
        getattr(rail, "type", None) == "input" and getattr(rail, "stop", False)
        for rail in (activated or [])
    )


def run_guarded_agent(
    transaction: Transaction,
    *,
    backend: ToolCallingBackend | None = None,
    ledger: Ledger | None = None,
) -> AgentRun:
    """The KS-0302 PATCH: run the agent behind the NeMo Guardrails input rail.

    The rail vets the untrusted memo BEFORE the model is called. On an injection
    hit the run is refused — no model call, no tool, no ledger write, `blocked`
    True — closing the memo-injection hole. Otherwise the normal (unguarded) agent
    runs, so a benign memo and a legitimate transfer still work.
    """
    if is_blocked(transaction.memo):
        return AgentRun(
            transaction=transaction,
            tool_calls=(),
            transfer_intents=(),
            content=GUARD_REFUSAL,
            blocked=True,
        )
    return run_agent(transaction, backend=backend, ledger=ledger)
