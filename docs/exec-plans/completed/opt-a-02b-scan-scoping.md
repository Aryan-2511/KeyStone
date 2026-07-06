# Exec-plan: OPT-A-02b — Live scan-scoping + granular --live flags

- **Slug:** `opt-a-02b-scan-scoping`
- **Feature IDs:** KS-0619 (upgrades KS-0617 / KS-0616 wiring)
- **Status:** done (PR pushed, awaiting review — not self-merged)
- **Started:** 2026-07-04
- **Owner (session):** Claude (Opus 4.8)

## Goal & acceptance

OPT-A-02 found deep Garak probes are intractable (LatentWhois ~1550s, `*Full` ~955s+, one
>1800s timeout, full sequence = hours); OPT-A-01b hit the pain — `keystone demo --live`
launched the hours-long red-team scan even when only live triage was wanted. Two bounded
fixes: (1) smart scan scoping — the default live red-team scans only the TRACTABLE probes
(minutes), with `--deep` opt-in for the full set; (2) granular flags so each agent's live
mode is independently controllable. NO change to agent decision logic, the policy, schema
meaning, the fallback, tagging semantics, or the boundary. Stop at green.

## Context / constraints

- Tractable/deep classified from the REAL OPT-A-02 timings only (ADR-0025 / OPEN_QUESTIONS
  Finding 2 + the `_OPT_A_02_CAPTURES` prompt counts) — nothing invented.
- Offline/recorded stays the default (data-residency front door; works with no Garak/Ollama).
- The policy's selection LOGIC and full capability are unchanged — scoping bounds the
  DEFAULT live scan set; `--deep` / SCOPE_FULL still exercises the whole catalog.

## Plan

- [x] Model/garak check: qwen2.5:3b (11.0s round-trip) + garak 0.15.1. Base main green (508).
- [x] PART 1 — classify DEEP_PROBES (`*Full` + LatentWhois) from real timings; `tractable_catalog()`;
      `SCOPE_TRACTABLE`/`SCOPE_FULL`; `live_red_team(scope=...)` bounds the live scan; trace +
      view gain `scan_scope` (no schema bump — default "full"). `build_red_team_view(deep=...)`.
- [x] PART 2 — granular CLI flags: `--live-triage`, `--live-redteam`, `--deep`; `--live` = both
      (tractable). Runner takes a `LiveModes(triage, redteam, deep)` bundle; default all-offline.
- [x] Tests: tractable-default fires no deep probe; `--deep` includes them; scan_scope tags;
      **`--live-triage` triggers NO red-team scan** (the OPT-A-01b pain, pinned).
- [x] Regenerate recorded_run.json (recorded==fresh; scan_scope="full", source recorded_profile).
- [x] Gates: make check green (503 passed). Offline front door 1.2s; --live-triage 12.9s (no scan).
- [x] Real garak_live proof: `live_red_team(budget=2)` → source=garak_live, scan_scope=tractable,
      no deep probe (~33s). A full tractable run scanned many tractable probes over ~24m (no
      single 30-min monster — scoping confirmed) then cleanly fell back on a transient GarakError.
- [x] Docs: ADR-0027, OPEN_QUESTIONS, feature_list KS-0619, MEMORY; make verify green
      (515 passed / 2 skipped, coverage 93.49%, pip-audit clean); committed + pushed (a168f44).

## Progress log

- 2026-07-04 branched off clean main (PR #43/#44 merged; baseline verify green). Confirmed
  `keystone demo --live` couples both agents (build_red_team_view + build_triage_view share one
  `live`), and the deep probes are what makes red-team live intractable.
- 2026-07-04 classified DEEP_PROBES from real data; added scope plumbing + granular flags +
  LiveModes bundle; kept run_red_team/live_red_team within the arg-count gate (scope stamped via
  model_copy; dropped the unused `profile` param). Regenerated the recorded run.
- 2026-07-04 PROOF: `--live-triage` = 12.9s, reasoner llm:qwen2.5:3b, red-team source
  recorded_profile (NO scan) — the OPT-A-01b pain fixed. Offline front door unchanged (1.2s).

## Decisions

- **Tractable vs deep from REAL timings.** DEEP = the `*Full` variants + `LatentWhois` (168
  prompts/~1550s; EnFrFull 270 prompts/~955s+; one >1800s timeout). Tractable = the rest
  (≤~24 prompts, ~45–145s). Cited to ADR-0025 + `_OPT_A_02_CAPTURES`.
- **Scoping bounds the DEFAULT live scan, not the selection space.** `live_red_team(scope)`
  passes a scoped CATALOG to the unchanged policy; the full catalog and `choose_next` logic are
  untouched; `--deep` runs the whole space. Scoped-out = not-run (never a fabricated result).
- **`scan_scope` is additive, no schema bump** (default "full" — a pre-scoping / offline run had
  the whole catalog available). Mirrors the OPT-A-02 `source` no-bump pattern.
- **`--live` redefined** = both agents live with the red-team TRACTABLE (was: full/hours).
  Granular `--live-triage` / `--live-redteam` (+`--deep`) control each independently.

## Open questions / blockers

- The tractable set is still ~10–25 min (11 real scans); "minutes not hours" is the honest
  bound, not "fast". The deep set remains the documented compute frontier (unchanged).

## Handoff (to fill on finish)

- **Changed:** `keystone.agents.red_team` (DEEP_PROBES/tractable_catalog/scope/scan_scope),
  `demo/red_team.py` (deep=), `demo/run_result.py` (RedTeamView.scan_scope), `demo/runner.py`
  (LiveModes), `demo/narrate.py` (scope in footer), `__main__.py` (granular flags),
  `recorded_run.json`; `tests/test_red_team_live.py`; docs.
- **Unchanged (sacred):** agent decision logic (policy `choose_next`, triage routing), the
  fallback mechanism, source/reasoner tagging semantics, the memo-blind boundary, offline default.
- **Verified:** make check / make verify green (515 passed / 2 skipped, coverage 93.49%,
  pip-audit clean, mypy strict / Ruff / import-linter clean, AST boundary scan passes). Real
  proofs captured (see Progress log). PR pushed to `opt-a-02b-scan-scoping`; NOT self-merged.
- **Honest caveat:** a full tractable run is still ~10–25 min (11 real scans) and can hit a
  transient GarakError → clean recorded_profile fallback; "tractable" = minutes, not fast. The
  deep probes remain the documented compute frontier (ADR-0025/0027).
