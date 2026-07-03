# Exec-plan: OPT-A-01 — Live Triage Agent (LLM-reasoned routing, safe by fallback)

- **Slug:** `opt-a-01-triage-live`
- **Feature IDs:** KS-0616 (upgrades KS-0613)
- **Status:** done
- **Started:** 2026-07-03
- **Owner (session):** Claude (Opus 4.8)

## Goal & acceptance

Take the Triage Agent from a transparent policy to genuine LLM reasoning (qwen2.5:3b via
Ollama) as an **opt-in live mode**. Offline console arc stays the default and stays
deterministic. Live is strictly additive: the LLM reasons when available, falls back to
the proven policy otherwise, and the record ALWAYS states which reasoner ran. Design
contract: `OPTION-A-00_TRIAGE_LIVE_DESIGN.md`. Acceptance = KS-0616 `done_criteria`.

## Context / constraints

- Contract: `OPTION-A-00_TRIAGE_LIVE_DESIGN.md` (§2 what live means, §3 model+fallback,
  §4 record/replay + the sacred boundary, §5 honesty tests + open evaluation).
- Binds: ADR-0008 (only the edge calls an LLM — reuse `keystone.llm.inference.complete`),
  ADR-0016 (memo-blind boundary sacred), ADR-0017 (Option B before A). New: **ADR-0021**.
- The policy (`route_for`) becomes the FALLBACK, not deleted. No new LLM client.

## Plan

- [x] Confirm qwen2.5:3b responds via Ollama (round-trip ~8.9s first call).
- [x] LLM reasoner: prompt (signals only) → parse+validate to exactly one of 3 routes.
- [x] Fallback + reasoner tagging (`policy` / `policy_fallback` / `llm:<model>`).
- [x] Opt-in wiring: `--live` on `keystone demo`; default stays offline.
- [x] Schema check: no bump — `TriageView.reasoner` defaults to `"policy"`. Regenerate
      `recorded_run.json` (recorded==fresh, offline).
- [x] Three honesty tests + interplay + offline-default + boundary (`test_triage_live.py`).
- [x] Evaluation surface: `scripts/triage_llm_eval.py`, `make triage-eval`.
- [x] Verify: `make check` / `make verify` green.
- [x] Update `feature_list.json` (KS-0616 done), ROADMAP, MEMORY, DECISIONS.

## Progress log

- 2026-07-03 created plan; confirmed model round-trip + disk; committed the design doc.
- 2026-07-03 built the live reasoner + fallback + tags in `keystone.agents.triage`; wired
  `--live` through demo/runner/CLI; added `reasoner` to `TriageView` (no schema bump).
- 2026-07-03 wrote `tests/test_triage_live.py` (22 fast + 1 slow real-qwen); all green.
- 2026-07-03 ran the real evaluation — the honest 3B finding (see Decisions); `make verify`
  green (495 passed, 2 skipped, coverage 93.49%, pip-audit clean, import-linter KEPT).

## Decisions

- **No schema bump.** `TriageView.reasoner` defaults to `"policy"`; a run recorded before
  live existed genuinely WAS a policy run, so old v7 data still loads truthfully. (ADR-0021.)
- **Fallback is the safety architecture** (not optional) and the **record is honest by
  tag** — a fallback is never reported as an LLM decision. (ADR-0021.)
- **The LLM sees signals only** — boundary sacred; AST import-scan still passes. (ADR-0016.)

## Open questions / blockers

- **The 3B reliability question, answered empirically (honest, negative).** In the
  evaluation, qwen2.5:3b did NOT honor the signal interplay: it collapsed toward
  `remediate` and repeatedly misread the numeric `failure_rate` (called 0.83 "no failure
  rate"). Bounded selection held (always a valid route, never invented), but selection
  QUALITY was poor. The policy remains the trustworthy default and fallback. Tracked in
  `OPEN_QUESTIONS.md` §B / ADR-0021.

## Next steps (resume here)

OPT-A-02: take the Red-Team Agent live (real Garak + optional LLM probe selection), the
heavier build — informed by the OPT-A-01 finding that 3B does bounded selection but reasons
poorly over numeric signals, so keep a deterministic fallback and record which ran.

## Handoff

- **Changed:** `keystone.agents.triage` (live reasoner, fallback, tags), `demo/triage.py`,
  `demo/runner.py`, `__main__.py` (`--live`), `demo/narrate.py` (honest reasoner line),
  `demo/run_result.py` (`TriageView.reasoner`, no bump), `recorded_run.json` (regenerated),
  `tests/test_triage_live.py`, `scripts/triage_llm_eval.py`, `Makefile` (`triage-eval`);
  docs: feature_list KS-0616, ROADMAP, MEMORY, DECISIONS ADR-0021, this plan.
- **Verified:** `make verify` green — 495 passed / 2 skipped, coverage 93.49%, pip-audit
  clean, mypy strict clean, Ruff clean, import-linter KEPT. Real live example produced
  (`keystone demo --live`): for (rate=0.83, seam=clean, sev=HIGH) the LLM chose REMEDIATE
  (policy: ESCALATE) — a genuine, recorded, differing decision.
- **Deferred:** trusting the LLM over the policy (open evaluation says don't, on 3B);
  NIM-hosted path (built for Ollama; NIM is a later reliability comparison).
- **Recommended next:** OPT-A-02 (live Red-Team Agent).
