# Exec-plan: DIAGRAMS-01 — Mermaid architecture/seam/loop diagrams

- **Slug:** `diagrams-01-mermaid`
- **Feature IDs:** (none — docs augmentation; see the feature_list note below)
- **Status:** done (PR pushed, awaiting review — not self-merged)
- **Started:** 2026-07-07
- **Owner (session):** Claude (Opus 4.8)

## Goal & acceptance

Add three committed Mermaid diagrams that render natively on GitHub and match the just-
consolidated `ARCHITECTURE.md` EXACTLY (no doc-vs-diagram drift): (1) system architecture,
(2) the seam thesis, (3) the closed adversarial loop. Depict the REAL system — three genuine
agents, the real loop, observation-driven policies (not LLMs), memo-blind boundary, exact
product names, "hash-chained evidence ledger" (not blockchain). Docs-only; no code/behaviour
change. Acceptance = diagrams render (grammar-valid) + match the doc + gates green at the same
test count.

## What was done

- **Diagram 1 (system architecture)** → `ARCHITECTURE.md`, right after the Layers table:
  NeMo Agent Toolkit orchestrator → L3 obligation/control mapping · L2 AI Assurance (Red-Team +
  Triage + Defense) · L1 FATF transaction monitoring (memo-blind) → target under test
  (mock-payments-agent) → the seam → shared spine (NeMo Guardrails · memo-blind boundary ·
  hash-chained evidence ledger).
- **Diagram 2 (the seam)** → `ARCHITECTURE.md`, new "## The seam (the thesis)" section: the AI
  side (Red-Team finds prompt-injection) and the financial side (FATF flags STRUCTURING) both
  bind to ONE event (TXN-000016); the memo-blind boundary keeps them independent.
- **Diagram 3 (the adversarial loop)** → `ARCHITECTURE.md`, new "## The multi-agent adversarial
  loop" section: Red-Team (exploit lands 11/12) → Triage (routes) → Defense (picks (a)/(c)) →
  re-scan patched target (0/12) → Red-Team adapts. Honest note: policies not LLMs, humans govern.
- **README** "Where to look" now flags that ARCHITECTURE.md carries the three diagrams.

## Decisions

- **Render-verification.** GitHub renders Mermaid natively; `mmdc` needs a headless browser that
  won't launch in this environment (STATUS_DLL_INIT_FAILED). Instead validated the GRAMMAR
  headlessly with **mermaid's own parser** (`mermaid.parse()` under jsdom, in a throwaway temp
  node project outside the repo): all three `.mmd` sources AND the three blocks re-extracted from
  `ARCHITECTURE.md` returned OK (exit 0). Conservative, GitHub-safe syntax (quoted labels,
  `flowchart TD/LR`, subgraphs, standard shapes).
- **No feature_list KS entry.** The diagrams are doc augmentation, not a shipped code feature; a
  "done" KS entry requires a cited test, and this task is **docs-only (no test change allowed)** —
  adding a test to justify a KS entry would violate the task's scope. Noted in MEMORY / TASKS /
  this plan instead (same precedent as the final-consolidation docs task).
- **Layer labels** use the task's descriptive names (L1 Transaction Monitor / L2 AI Assurance /
  L3 Obligation mapping) tied to the doc's semantics (code tags L1=FATF, L2=AI-security; M2-00
  defines L3=governance/obligations) — no contradiction with `ARCHITECTURE.md`.

## Verify

- All three Mermaid blocks grammar-valid (mermaid.parse under jsdom, OK).
- Diff is `ARCHITECTURE.md` + `README.md` only — no src/tests/schema touched.
- `make check` / `make verify` green at the **same** count as the base (547 passed, 2 skipped);
  docs-consistency test (links + ADR index) passes; mypy / Ruff / import-linter clean.

## Handoff

- **Changed:** `ARCHITECTURE.md` (3 mermaid diagrams + two new sections), `README.md` (pointer);
  docs: MEMORY, TASKS, this plan.
- **Unchanged:** all code, tests, schema, behaviour. Docs-only.
