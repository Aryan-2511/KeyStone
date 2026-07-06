# FINAL_STATE_AUDIT.md — the completed-system audit (final consolidation)

> **What this is.** A read-only audit of Keystone as a **finished artifact** — the
> multi-agent architecture is COMPLETE (three agents + the closed adversarial loop, MC-02
> merged, #49). Every item is classified **CLEAN / STALE / MESSY / UNCLEAR** with a
> `file:line` cite. This audit was written BEFORE any reconciliation; the "Reconciled"
> column records what the same PR then fixed. It **supersedes** the earlier
> [`CONSOLIDATION_AUDIT.md`](CONSOLIDATION_AUDIT.md) (a snapshot from an earlier state,
> kept as history).
>
> **Scope discipline:** docs truth-ups, dead-file review, and safe tidies only. NO
> system/behaviour/schema/agent-logic change. Risky reorgs are **flagged, not done**.

## Verdict

The **code and the primary governance set are current and honest**; the two reviewer-facing
**overview docs (ARCHITECTURE.md, README.md) and ARTIFACT_INDEX.md were STALE** — they
described the *two-agent* system and had not caught up to the Defense Agent (MC-01) or the
closed adversarial loop (MC-02). Those are content truth-ups (done in Phase 2). No dead files,
no honesty overclaims, no broken ADR sequence, no risky reorg required.

---

## A. Architecture truth — ARCHITECTURE.md

| Item | Status | Evidence | Reconciled |
| --- | --- | --- | --- |
| Describes all THREE agents | **STALE** | `ARCHITECTURE.md:21-22` "two genuine agents in a supervisor–worker topology — a Red-Team Agent … and a Triage Agent"; `:37` Agents-layer row lists only Red-Team + Triage; `:4` header "both agents are built" | ✅ truth-up to three agents |
| The closed adversarial loop (MC-02) | **STALE** | absent from the data-flow (`:66-72`) — no defense / re-scan / adapt | ✅ added to data-flow |
| The remediation menu {(a),(c)} + two-sided seam | **STALE** | not mentioned | ✅ added |
| Layers / determinism table | CLEAN (but Agents row stale) | `:30-38` — layers accurate | ✅ Agents row updated |
| ADR links, inference switch, ledger, boundary | CLEAN | `:42-49,51-62` accurate | — |

## B. Folder structure — mentor-navigable?

| Item | Status | Evidence |
| --- | --- | --- |
| `src/keystone/` layout | **CLEAN** | `agents/` (red_team, triage, defense, adversarial + orchestrator/run = the NAT chassis), `assurance/` (seam, remediation, guard, garak_*, framework, loop), `core/` (fatf, ledger, transactions, obligations, controls, reporting), `demo/` (per-agent builders + runner + narrate), `llm/`, `ui/`, `convergence/`. Logical; the agents, remediations, arc, seam, ledger, harness are each easy to find. |
| Design docs at repo root | **CLEAN** | `M1-00`/`M2-00`/`MA-00`/`MB-00`/`MC-00`/`OPTION-A-00`/`OPTION-A-02-00` — consistent with the existing convention (all design docs at root). |
| `docs/` layout | **CLEAN** | `docs/{design,exec-plans/{active,completed},assets,references,generated}` — clear. |
| 5 recent exec-plans loose in `docs/exec-plans/` root | **MESSY (safe tidy)** | `mc-01`, `mc-02`, `mc-pre-01`, `opt-a-01b`, `opt-a-02b` are done but sit in the root, not `completed/` (the convention, `docs/exec-plans/README.md:11`). No doc references their paths (safe). → **moved to `completed/`** |
| `src/keystone/policy/` | **MESSY (flag-only)** | placeholder package; docstring says *"Empty until Phase 2"* (`policy/__init__.py`) — Phase 2 is long past and the rails actually live in `assurance/guardrails/`. Harmless; removing/renaming it is an import-touching change → **flag-only, not done** (see Recommended future reorgs). |

## C. Harness coherence

| Item | Status | Evidence | Reconciled |
| --- | --- | --- | --- |
| ADR sequence + index rows | **CLEAN** | 30 index rows = 30 `## ADR-00NN` headers; sequence 0001–0030 complete, no gaps/dupes (`tests/test_docs.py` also pins this) | — |
| CLAUDE.md | **CLEAN** | updated in MC-02 to "complete multi-agent system … three genuine agents … Movements A/B/C done" | — |
| MEMORY / DECISIONS / OPEN_QUESTIONS / ROADMAP / TASKS / feature_list | **CLEAN** | all carry the MC-01/MC-02 entries (ADR-0029/0030, KS-0621/0622); ROADMAP/TASKS mark Movement C complete | — |
| README.md | **STALE** | `:9,21,23` "two genuine agents"; `:43-44` lists "Movement C (a defense agent …)" as *deferred* though it is DONE; `:58-59` "the two agents"; `:67-68` status "both agents (Movements A/B)" | ✅ truth-up |
| ARTIFACT_INDEX.md | **STALE** | design-records table (`:26-29`) omits `MC-00`, `OPTION-A-00`, `OPTION-A-02-00`; probes (`:35-36`) omit `remediation_probe.md`; `:44` "ADR-0015–0020" (now 0030); no three-agent/loop mention | ✅ truth-up |
| make targets | **CLEAN** | `setup/format/lint/typecheck/arch/test/test-all/audit/check/verify/phase-check/milestone/demo/triage-eval/ui/clean` all real; `demo/ui/check/verify/triage-eval` documented in `CLAUDE.md`. (`--deep` is a `keystone demo` **CLI flag**, not a make target — no gap.) |
| CONSOLIDATION_AUDIT.md | **HISTORICAL** | an earlier consolidation's audit (references ADR-0015–0020); not wrong, superseded by this doc — kept as history |

## D. Dead files / scratch / cruft

| Item | Status | Evidence |
| --- | --- | --- |
| `*.bak` / `*.orig` / `*.tmp` / `scratch*` | **CLEAN (none)** | repo-wide find returns nothing |
| Ignored artifacts (`.env`, `build/`, `.import_linter_cache/`, `.claude/settings.local.json`, caches) | **CLEAN** | all git-**ignored** (`git status --ignored` `!!`), none committed |
| Leftover duplicate design doc | **CLEAN (already removed)** | the `docs/MC-00…` duplicate was removed in MC-01; only the root `MC-00_DEFENSE_AGENT_DESIGN.md` remains |

**Nothing was deleted** — there was no delete-safe cruft to remove.

## E. The reviewer's front door

| Item | Status | Evidence | Reconciled |
| --- | --- | --- | --- |
| README "Start here" runs | CLEAN | `uv run keystone demo` is the front door (`README.md:46-50`) | — |
| … describes the COMPLETE system | **STALE** | describes two agents; omits the Defense Agent + the loop finale | ✅ (with the README truth-up) |
| `keystone demo` shows the finale (4c) | **CLEAN** | the narration prints `4c. Adversarial loop - offense re-tests defense (MC-02)` with the measured 11/12 → 0/12 re-scan (verified this run) | — |

## F. Final honesty sweep

| Item | Status | Evidence |
| --- | --- | --- |
| Three agents / closed loop / memo-blind / compute-gated frontier | **CLEAN** | accurately claimed in the current governance docs (post-MC updates); the stale overview docs *under*-claimed (two agents), never over-claimed |
| "10 instruments / 3 jurisdictions" vs code's 6/2 | **CLEAN (hedged everywhere)** | `OPEN_QUESTIONS.md:13-14` §A1 (the open item); `ARTIFACT_INDEX.md:14,18` (deck=10/3, code=6/2); `CONSOLIDATION_AUDIT.md:64-65,117-123`. **No committed doc asserts 10/3 as repo truth.** |
| Any other numeric/capability claim not backed by code | **CLEAN (none found)** | the live-agent findings, the loop measurement (11/12→0/12 recorded, 11/12→0/4 live), and the compute frontier are all cited to code/tests |

---

## Recommended future reorgs (flag-only — each needs its own decision + PR)

1. **Remove or repurpose `src/keystone/policy/`.** It is an empty placeholder whose stated
   role ("Guardrails rails") is actually filled by `keystone.assurance.guardrails`. **Blast
   radius:** small but import-touching — it is referenced by the import-linter contract's
   layer set and `docs/design/architecture-boundaries.md`; deleting it means updating those.
   Not done here (audit-first: no import-rippling moves).

2. **(Optional) Fold the root design docs under `docs/design/`.** Seven `*-00_*_DESIGN.md`
   files at the repo root are the established convention, but a mentor might expect them under
   `docs/`. **Blast radius:** every relative link to them (README, ARTIFACT_INDEX, ADRs,
   MEMORY) + `test_docs.py::test_no_broken_relative_links`. A large link-rewrite — deliberately
   **not** done; flagged for a decision.

## UNCLEAR items for you to decide

- **`CONSOLIDATION_AUDIT.md` vs `FINAL_STATE_AUDIT.md`.** Two audit docs now exist. This one
  supersedes the earlier snapshot; kept the old one as history and pointed ARTIFACT_INDEX at
  both. If you'd rather have one, say so and I'll archive the older under `docs/`.
- **`policy/` placeholder** (item 1 above) — keep as an intentional layer marker, or remove?
