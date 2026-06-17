<!--
Exec-plan (completed). KS-0204 — first live inference at the LLM edge.
-->

# Exec-plan: LLM-edge obligation-summary phrasing (KS-0204)

- **Slug:** `summary-phrasing`
- **Feature IDs:** KS-0204 (Phase 2 / Layer 3). First live call from
  `keystone.llm.inference`; NIM backend only.
- **Status:** done (archived 2026-06-18)
- **Started:** 2026-06-18
- **Owner (session):** agent
- **Branched from:** `main` @ 6e08c47 (KS-0202 merged; `make verify` green).

## Goal & acceptance

An edge-side `phrase_summary(obligation) -> str` rewords the curated `summary`
for readability via NIM, faithfully (no added/altered facts), without writing
core data. ADR-0012 §4 (summary = system of record; phrasing is a separate edge
transform) and ADR-0008 (only the edge calls an LLM; import-linter keeps core
LLM-free). KS-0204 done_criterion: summaries produced at the edge while the
import boundary keeps graph/crosswalk logic LLM-free.

## What shipped

- `keystone/llm/phrasing.py`: `phrase_summary` + `_phrasing_backend()` (NIM pinned
  to `nvidia/nvidia-nemotron-nano-9b-v2`, `/no_think` system prompt + faithfulness
  contract, temp 0.2 / top_p 0.9 / max_tokens 256). Exported from `keystone.llm`.
- `keystone/llm/inference/nim.py`: `NimBackend` gained `temperature`/`top_p`/
  `max_tokens` fields (defaults preserve prior behavior); sends `stream:false` +
  these in the payload. Protocol + Ollama untouched.
- `tests/test_phrasing.py`: FAST (fake backend / mocked httpx) — prompt
  construction (`/no_think` + faithfulness), param pass-through on the wire,
  canned→stripped string, unreachable-backend propagation, MANDATORY no-mutation;
  SLOW — one live NIM test that `skipif`s when `NVIDIA_API_KEY` unset.
- feature_list KS-0204 → done + tests; TASKS.md + MEMORY.md updated.

## Decisions

- Probe + feature call NIM via **httpx** (existing seam, same OpenAI-compatible
  endpoint), not the openai SDK (not a dep) — user-confirmed.
- Sampling params live on the `NimBackend` instance, not the `complete()`
  signature → no Protocol/Ollama churn. No new ADR (implements ADR-0012 §4).
- No caching (live-on-demand), per task.

## Verification

- Step-1 no-think sanity probe: PASS — content only, no preamble, empty
  `reasoning_content`.
- `make check` (fast, fake backend, no key/network): exit 0, 91 passed,
  2 deselected, coverage 92.8% (`phrasing.py` 100%).
- `uv run pytest -m slow`: SKIPS cleanly with no key (exit 0 under `--no-cov`);
  with key loaded from `.env`, live phrasing test PASSES.
- import-linter: core→edge contract KEPT. `obligations.json` byte-identical.

## Deferred / next

- Ollama / offline-demo fallback for phrasing NOT wired (NIM only).
- Next task: **KS-0203** (EU hard-law vs India self-certification modality
  contrast) — reads `ControlMapping.modalities` (already preserved by KS-0202).

## Handoff

Branch `ks-0204-summary-phrasing` (from main 6e08c47). Pushed; PR opened for
review (NOT self-merged). Faithfulness sample pairs (EU + India) reported to the
reviewer. See [[MEMORY.md]] for the NIM payload/response shape + no-think result.
