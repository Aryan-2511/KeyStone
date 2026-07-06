# Exec-plan: OPT-A-01b — Triage LLM prompt-rescue (model or prompt?)

- **Slug:** `opt-a-01b-triage-prompt-rescue`
- **Feature IDs:** KS-0618 (revisits KS-0616 / ADR-0021)
- **Status:** done (awaiting review — PR open, not self-merged)
- **Started:** 2026-07-04
- **Owner (session):** Claude (Opus 4.8)

## Goal & acceptance

OPT-A-01 found qwen2.5:3b routed poorly (1/6 agree, collapsed to one route, misread the
numeric `failure_rate`). That is as consistent with a WEAK PROMPT as a weak model. Before
"3B can't do it" is settled, make a GENUINE prompt-engineering effort and re-run the SAME
evaluation. Change the PROMPT + the eval ONLY — never the policy, fallback, tagging,
boundary, schema, or the opt-in default. Stop at green + an honest before/after.

## Context / constraints

- Revisits ADR-0021's honest-negative 3B finding; policy `route_for` is the GROUND TRUTH
  (unchanged) and the source of the few-shot examples.
- Boundary (OPT-A-00 §4) SACRED: prompt carries the three SIGNALS only — never memo /
  attack channel. Few-shot examples are signal→route pairs, never attack text.
- 3B only (no 8B escalation). Policy stays the default regardless of the result.

## Plan

- [x] Model check: qwen2.5:3b up via Ollama (18.3s cold round-trip).
- [x] Rewrite the prompt with the four levers (signal clarity, taught rules, few-shot,
      structured output). Verify every few-shot example matches `route_for`.
- [x] Re-run the SAME eval (`make triage-eval`): before 1/6 → after **6/6** (30/30 at 5×).
- [x] **Held-out anti-parrot probe** (new): (seam,severity)+rate combos the examples never
      show, built so a parrot fails → **4/6 (12/18)**. This is the decisive rigor step.
- [x] Mechanical guard test: few-shot examples must match `route_for` + be held-out from
      the eval tuples. Existing honesty/boundary/constrained-output tests still pass.
- [x] Real `live_triage` example on the arc finding with the new prompt.
- [x] Docs: ADR-0026, OPEN_QUESTIONS Finding 1 refinement, feature_list KS-0618, this plan.
- [x] Gates: `make check` / `make verify` green.

## Progress log

- 2026-07-04 confirmed model round-trip; audited the already-drafted prompt rewrite.
- 2026-07-04 ran the in-distribution eval: 6/6 agree (18/18 at 3×, 30/30 at 5×) — a huge
  reversal of OPT-A-01's 1/6. Suspected few-shot proximity (interplay scenarios mirror the
  worked examples' seam/severity, only the rate differs) + parroted rationales (arc case:
  right route, "open seam" reason on a CLEAN seam).
- 2026-07-04 built + ran a held-out anti-parrot probe → **4/6**. Two stable failures:
  0.25 clean LOW → said accept (misapplied "contained" to a clean seam); 0.06 open MED →
  said escalate, rationale "above 0.10" (misread 0.06 — the OPT-A-01 failure, resurfaced).
- 2026-07-04 folded the held-out probe into `make triage-eval`; added guard tests; wrote docs.

## Decisions

- **Honest verdict = BOTH at once (the truthful reconciliation).** The failure was PARTLY a
  prompt artifact — signal clarity + few-shot lifted in-distribution accuracy 1/6 → 6/6 — AND
  the model ceiling is real: on held-out combos 3B drops to 4/6, still misreads the rate and
  misapplies seam semantics. It pattern-matches the examples; it does not robustly apply the
  rules. → **policy stays the default, now with STRONGER evidence** (ADR-0026).
- **Promotion NOT taken.** The 6/6 headline alone looked "trustworthy" (a STOP-and-ask
  trigger); the held-out probe dissolved that — 3B is not reliable enough to promote. The
  default-promotion question is explicitly deferred to a joint call; not flipped here.
- **The held-out probe is now a permanent, reproducible part of the eval** — a 6/6 that hides
  a held-out 4/6 must never again read as "trustworthy."

## Open questions / blockers

- Whether the improved-but-capped 3B is ever worth an opt-in *recommended* mode is a separate
  decision (deferred, joint). The compute ask (purpose-fine-tuned small model) is UNCHANGED
  and now better-evidenced: prompt effort helps in-distribution, the ceiling is the model.

## Next steps (resume here)

- Human review of the PR. If accepted, no promotion of the default follows automatically.
- Frontier remains: a fine-tuned small on-prem model for the bounded routing task (OPEN_QUESTIONS §B).

## Handoff

- **Changed:** `keystone/agents/triage.py` (prompt: `TRIAGE_SYSTEM` + `build_live_prompt`,
  the four levers), `scripts/triage_llm_eval.py` (held-out anti-parrot block, refactor),
  `tests/test_triage_live.py` (few-shot fidelity + held-out guards); docs: DECISIONS
  ADR-0026, OPEN_QUESTIONS Finding 1, feature_list KS-0618, this plan.
- **Unchanged (sacred):** policy `route_for`, fallback, reasoner-tagging, memo-blind
  boundary, schema, the opt-in default. Policy is still the default reasoner.
- **Verified:** `make check` / `make verify` green; boundary AST scan passes; eval reproduces
  in-distribution 6/6 + held-out 4/6.
