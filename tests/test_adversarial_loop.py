"""The closed adversarial loop (MC-02) — offense → defense → re-scan → adapt.

Keystone's finale: after the Defense Agent patches, the Red-Team RE-SCANS the patched target
and adapts. These tests pin the guarantees the design fixed (MC-00 §4):

1. **The loop closes (before/after-patch)** — the exploit lands on the unpatched target and the
   re-scan of the PATCHED target shows the changed outcome (the patch mitigated it). MEASURED,
   not assumed; if a patch did NOT change the outcome, that is reported (a real finding).
2. **The Red-Team adapts** — its selection responds to the post-patch observation (it abandons a
   closed surface / pivots to an open family — the MA-00 §2 agency, now over post-patch outcomes).
3. **(a) real re-scan vs (c) offline re-verify** — handled honestly (different `kind`/`source`).
4. **Exercisable offline** — the loop replays the recorded guarded profile, no Garak/Ollama.

Deterministic, fast-gated — no LLM, no network, no Garak.
"""

from __future__ import annotations

import ast
import datetime
import importlib
import shutil
from pathlib import Path

import httpx
import pytest

from keystone.agents.adversarial import (
    RECORDED_GUARDED_PROFILE,
    close_loop,
    guarded_observe,
)
from keystone.agents.defense import DefenseDecision, DefenseSignals, defend
from keystone.agents.red_team import (
    PROBE_CATALOG,
    RECORDED_DEFENSE_PROFILE,
    RedTeamTrace,
    profile_observe,
    run_red_team,
)
from keystone.agents.triage import FindingSeverity, SeamClassification
from keystone.assurance.referenced import REFERENCED_ASSURANCE
from keystone.assurance.remediation import RemediationContext, SeamSide
from keystone.core.transactions import Currency, Transaction, TransactionType


def _exploit_trace() -> RedTeamTrace:
    """A real Red-Team trace that exploits latentinjection over the recorded profile."""
    return run_red_team(profile_observe(RECORDED_DEFENSE_PROFILE))


def _guardrail_decision() -> DefenseDecision:
    """An (a)-favoring Defense decision (injection live, no financial gap) → GUARDRAIL_PATCH."""
    return defend(
        DefenseSignals(
            failure_rate=0.90,
            financial_gap=False,
            seam_result=SeamClassification.CLEAN,
            severity=FindingSeverity.HIGH,
        ),
        context=RemediationContext(operative_tx_id="TXN-000016"),
    )


# --- 1. THE LOOP CLOSES: before/after-patch (the whole point) ------------------


def test_loop_closes_exploit_lands_then_patched_rescan_mitigates() -> None:
    trace = _exploit_trace()
    loop = close_loop(trace, _guardrail_decision())  # offline recorded re-scan
    assert loop.side is SeamSide.AI and loop.kind == "ai_rescan"
    # Exploit LANDED on the unpatched target...
    assert loop.pre_patch_fails > 0
    # ...and the re-scan of the PATCHED (guarded) target shows it no longer lands.
    assert loop.post_patch_fails == 0
    assert loop.mitigated is True
    assert loop.source == "recorded_profile"  # offline re-scan, honestly tagged


def test_recorded_guarded_profile_is_anchored_to_the_proven_result() -> None:
    # The post-patch profile is anchored to REFERENCED_ASSURANCE (the rail took the exploit to
    # after_fails == 0), not fabricated — every injection probe is blocked (0 fails).
    assert REFERENCED_ASSURANCE.after_fails == 0
    assert all(fails == 0 for fails, _ in RECORDED_GUARDED_PROFILE.values())
    assert set(RECORDED_GUARDED_PROFILE) == {
        p for fam in PROBE_CATALOG.values() for p in fam
    }


# --- 2. THE RED-TEAM ADAPTS to the post-patch observation ---------------------


def test_red_team_adapts_defense_held_when_the_surface_is_closed() -> None:
    # Post-patch the whole injection surface is blocked (the general rail); the Red-Team
    # re-runs, finds nothing lands, and ABANDONS it — pre-patch it exploited latentinjection,
    # post-patch it exploits nothing (the defense held). Its selection responded to the patch.
    trace = _exploit_trace()
    assert trace.exploited_family == "latentinjection"  # pre-patch
    loop = close_loop(trace, _guardrail_decision())
    assert loop.adapted_exploited_family is None  # post-patch: the surface is closed


def test_red_team_pivots_when_only_the_patched_family_is_closed() -> None:
    # The adaptation MECHANISM: if the patch closes ONLY the exploited family, the Red-Team
    # pivots to the family still getting through (the MA-00 §2 flip, over post-patch outcomes).
    partial = dict(RECORDED_DEFENSE_PROFILE)
    for probe in PROBE_CATALOG["latentinjection"]:
        partial[probe] = (0, 12)  # latent now blocked (patched)
    # promptinject left at its recorded (through) values.
    loop = close_loop(
        _exploit_trace(),
        _guardrail_decision(),
        guarded_profile=partial,
    )
    assert loop.adapted_exploited_family == "promptinject"  # pivoted to the open family


# --- the honest "patch did NOT mitigate" branch -------------------------------


def test_loop_reports_honestly_when_the_patch_does_not_mitigate() -> None:
    # If the re-scan shows the exploit STILL lands, the loop says so (not hidden). Model a
    # guarded profile where the exploited probe is unchanged (the patch failed to close it).
    unmitigated = dict(RECORDED_GUARDED_PROFILE)
    lead = PROBE_CATALOG["latentinjection"][0]
    unmitigated[lead] = RECORDED_DEFENSE_PROFILE[lead]  # still gets through
    loop = close_loop(
        _exploit_trace(), _guardrail_decision(), guarded_profile=unmitigated
    )
    assert loop.post_patch_fails and loop.post_patch_fails > 0
    assert loop.mitigated is False
    assert "STILL lands" in loop.adaptation


# --- 3. (a) real re-scan vs (c) OFFLINE re-verify (honest difference) ----------


def test_c_loop_is_an_offline_reverify_not_a_live_rescan() -> None:
    lone = Transaction(
        id="TXN-009001",
        timestamp=datetime.datetime(2026, 3, 1, tzinfo=datetime.UTC),
        sender_account="ACC-9001",
        recipient_account="ACC-0042",
        amount=9_000.0,
        currency=Currency.USD,
        tx_type=TransactionType.TRANSFER,
    )
    decision = defend(
        DefenseSignals(
            failure_rate=0.03,
            financial_gap=True,
            seam_result=SeamClassification.CLEAN,
            severity=FindingSeverity.HIGH,
        ),
        context=RemediationContext(stream=(lone,), operative_tx_id=lone.id),
    )
    loop = close_loop(_exploit_trace(), decision)
    assert loop.side is SeamSide.FINANCIAL and loop.kind == "financial_reverify"
    assert loop.source == "offline"  # NOT a live re-scan — described truthfully
    assert loop.post_patch_fails is None and loop.post_patch_total is None
    assert (
        loop.mitigated is True
    )  # the tightened detection covers the gap (offline-verified)
    assert "offline re-verify" in loop.adaptation


# --- 4. exercisable OFFLINE (no Garak/Ollama) ---------------------------------


def test_loop_needs_no_live_infra_offline() -> None:
    # The whole loop ran above with no `rescan_observe` injected — it replayed the recorded
    # guarded profile deterministically. Re-running yields the identical result (determinism).
    trace = _exploit_trace()
    a = close_loop(trace, _guardrail_decision())
    b = close_loop(trace, _guardrail_decision())
    assert (a.pre_patch_fails, a.post_patch_fails, a.mitigated) == (
        b.pre_patch_fails,
        b.post_patch_fails,
        b.mitigated,
    )


# --- 5. memo-blind (SACRED): the loop reaches no crime detector ---------------


def test_adversarial_module_reaches_no_crime_detector() -> None:
    # The loop is offense-side (the Red-Team re-scans a target); it must have no path to the
    # memo-blind crime detector. AST-scan the module's imports (the live guarded re-scan is
    # loaded via importlib, so nemoguardrails/Garak stay out of the offline import graph).
    module = importlib.import_module("keystone.agents.adversarial")
    assert module.__file__ is not None
    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
    for forbidden in (
        "keystone.core.fatf",
        "keystone.core.fatf.engine",
        "keystone.assurance.framework",  # project_financial / CrimeSide.detect (the lock)
        "keystone.assurance.injection_patterns",
    ):
        assert forbidden not in names, (
            f"the adversarial loop must not import {forbidden!r} — it is offense-side and "
            f"has no path to the crime detector (memo-blind, MC-00 §4)"
        )


# --- 6. the ONE real-Garak live re-scan (slow; MEASURES the guarded outcome) ---


def _ollama_up() -> bool:
    try:
        httpx.get("http://localhost:11434/api/tags", timeout=2.0)
    except httpx.HTTPError:
        return False
    return True


@pytest.mark.slow
def test_real_guarded_rescan_measures_the_post_patch_outcome() -> None:
    # A genuine re-scan of the PATCHED (guarded) target for the exploited lead probe. We do NOT
    # assume the patch works — we MEASURE it: the loop's post-patch outcome comes from a real
    # Garak scan of the guarded endpoint, and the source is tagged garak_live.
    if shutil.which("garak") is None and shutil.which("uv") is None:
        pytest.skip("garak CLI not available")
    if not _ollama_up():
        pytest.skip("Ollama not running")
    loop = close_loop(
        _exploit_trace(),
        _guardrail_decision(),
        rescan_observe=guarded_observe(report_prefix="mc02_test_rescan", prompt_cap=4),
    )
    assert loop.source == "garak_live"
    assert loop.post_patch_total is not None and loop.post_patch_total > 0
    # The measured outcome is honest either way (mitigated or not) — we just recorded reality.
    assert isinstance(loop.mitigated, bool)
