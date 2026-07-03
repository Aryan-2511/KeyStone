# Exec-plan: OPT-A-02-01 — Live Red-Team Agent (real Garak scans, full selected sequence)

- **Slug:** `opt-a-02-redteam-live`
- **Feature IDs:** KS-0617 (upgrades KS-0612)
- **Status:** done
- **Started:** 2026-07-03
- **Owner (session):** Claude (Opus 4.8)

## Goal & acceptance

Take the Red-Team Agent genuinely live: run its policy-selected probe sequence as REAL
Garak scans against the target, observe REAL outcomes, feed them to the adaptive policy —
as an opt-in mode. Offline console arc stays the deterministic default. Live is strictly
additive: real Garak when available, recorded-profile fallback otherwise, source-tagged.
Selection stays the policy (LLM-selection compute-gated per OPT-A-01). Run the FULL
selected sequence (no subset cap). Contract: `OPTION-A-02-00_REDTEAM_LIVE_DESIGN.md`.
Acceptance = KS-0617 `done_criteria`.

## Context / constraints

- Contract: `OPTION-A-02-00_REDTEAM_LIVE_DESIGN.md` (§2 live-Garak, §3 source + fallback,
  §4 record/replay + sacred boundary, §5 honesty tests + operational profile).
- Mirror OPT-A-01 (ADR-0021): opt-in flag, fallback-as-safety, honest tag (`reasoner` →
  `source`), offline-default preserved, no schema bump. Binds: ADR-0003 (Garak isolated
  subprocess — reuse `garak_observe`/`scan_mock_agent`, no new wrapper), ADR-0016
  (memo-blind boundary sacred). New: **ADR-0022**.
- Selection stays the policy — NO LLM-reasoned selection (compute-gated; OPT-A-01 evidence).

## Plan

- [x] Step -1 hard gate: Garak 0.15.1 runs; real smoke scan executed (8/8 got through,
      ~48s); target + Ollama reachable; disk 21G. NOT fell back.
- [x] `live_red_team`: full policy-selected sequence as real Garak; GarakError → complete
      recorded-profile fallback; `source` tag on `RedTeamTrace` (garak_live/recorded_profile).
- [x] Opt-in wiring: same `--live` flag drives both agents; `build_red_team_view(live)`;
      thread through runner. Default stays offline.
- [x] Schema: no bump — `RedTeamView.source` defaults to `recorded_profile`. Regenerate
      recorded_run.json (recorded==fresh, offline).
- [x] Honesty tests (`test_red_team_live.py`): source-honesty, fallback, agency-preserved,
      offline-default; slow real-Garak test. Boundary AST test still passes.
- [x] Real full live-scan proof + operational profile (per-probe + total wall-clock).
- [x] Verify gates; update feature_list KS-0617, ROADMAP, MEMORY, DECISIONS, OPEN_QUESTIONS.

## Progress log

- 2026-07-03 Step -1: Garak 0.15.1 confirmed; real smoke scan executed (not fell back).
  OPT-A-01 confirmed merged into main (PR #41); branched off clean main; committed design doc.
- 2026-07-03 built `live_red_team` + source tag + fallback; wired `--live` to both agents;
  added `RedTeamView.source` (no bump); narration shows source honestly.
- 2026-07-03 wrote `tests/test_red_team_live.py` (11 fast + 1 slow); all green; ran the real
  full live sequence for the operational profile.

## Decisions

- **No schema bump.** `RedTeamView.source` defaults to `recorded_profile` (a pre-live run
  genuinely WAS recorded). (ADR-0022.)
- **Whole-trace fallback.** On any GarakError the entire run falls back to a complete
  recorded-profile run (never a half-live/half-recorded trace) — one honest source tag.
- **Full sequence, offline stays at DEFAULT_BUDGET.** Live runs `FULL_BUDGET` (policy's own
  stop); the offline recorded demo stays at `DEFAULT_BUDGET=6` so the front door / UI / fixture
  are unchanged.
- **LLM-selection compute-gated** (OPT-A-01 evidence); OPEN_QUESTIONS §B. (ADR-0022.)

## Open questions / blockers

- **Live vs recorded is a real difference (honest finding).** Live, the target (qwen2.5:3b
  + the vulnerable system prompt) is exploited by BOTH families — `promptinject` gets through
  live (~11/12), whereas the recorded profile characterized it as blocked. The agent adapts to
  the REAL outcomes; the recorded profile is an anchored characterization, not a live capture.
  This is exactly why live mode is valuable and why the source tag matters.

## Next steps (resume here)

The live-agent frontier is honestly complete for current hardware. The remaining frontier is
**LLM-reasoned selection for BOTH agents** — evidence-backed (OPT-A-01) as blocked on capable
inference; the NVIDIA compute ask. A NIM-hosted (more capable model) path is the reliability
comparison that could unblock it.

## Handoff

- **Changed:** `keystone.agents.red_team` (live_red_team, source tag, mechanism_for, fallback),
  `agents/__init__.py`, `demo/red_team.py` (build_red_team_view(live)), `demo/runner.py`,
  `demo/narrate.py` (source + both-agent banner), `demo/run_result.py` (RedTeamView.source, no
  bump), `recorded_run.json` (regenerated), `__main__.py` (--live help), `tests/test_red_team_live.py`;
  docs: feature_list KS-0617, ROADMAP, MEMORY, DECISIONS ADR-0022, OPEN_QUESTIONS, this plan.
- **Verified:** make check / make verify green; real full live sequence executed (source
  garak_live) — the operational profile is in the PR.
- **Deferred:** LLM-reasoned probe selection (compute-gated, OPEN_QUESTIONS §B).
- **Recommended next:** LLM-reasoned selection once capable inference is available (NIM), or
  Movement C (defense agent, gated on a ≥2-remedy menu).
