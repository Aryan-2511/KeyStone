<!--
Exec-plan (completed). KS-0303 — Garak red-team probe (subprocess) finds the vuln.
-->

# Exec-plan: Garak red-team probe (KS-0303)

- **Slug:** `garak-probe`
- **Feature IDs:** KS-0303 (Phase 3 / Layer 2). `depends_on` KS-0301 (consumes its
  `MEMO_INJECTION_SIGNATURE`). Built BEFORE KS-0302 (Guardrails) — detector before
  patch (ADR-0011 amendment); KS-0302 now `depends_on` KS-0303.
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-19
- **Owner (session):** agent
- **Branched from:** `main` @ dc49179 (KS-0301 merged).

## Why

Layer 2's assurance loop needs the DETECTOR that finds the KS-0301 agent's
memo-injection flaw, mapped to OWASP + regulation, before the Guardrails patch
that will close it. Garak is the red-team scanner; it runs as an isolated
subprocess (ADR-0003), and the bulk of the logic is deterministic over a captured
report.

## What shipped (`keystone.assurance`)

- `garak_probe.py` — pinned to Garak **0.15.1**: `parse_report` (JSONL `eval`
  records → typed `GarakFinding`), the `FAMILY_MAPPINGS` data table
  (prompt-injection → OWASP LLM01 + Agentic ASI → EU Art. 15 / `OBL-EUAI-015` →
  India RBI sutra / `OBL-RBI-001`), `map_finding`, `found_our_vulnerability` (any
  prompt-injection hit, `fails>0`), `record_finding` (ledger `assurance_finding`),
  and the subprocess `run_scan`/`scan_mock_agent` (curated `latentinjection`
  subset, `soft_probe_prompt_cap`).
- `_targets/vuln_agent_target.py` — STANDALONE, stdlib-only Garak `function` target
  (Garak's isolated venv can't import keystone); calls Ollama under the vulnerable
  system prompt, put on PYTHONPATH by `scan_mock_agent`.
- `tests/fixtures/garak/` — captured real v0.15.1 reports: `*_vulnerable` (fails 10/12)
  and `*_clean` (fails 0/12).
- `tests/test_garak_probe.py` — fast tests over the fixtures (parser, mapping,
  found-our-vuln True/False, ledger shape, pinned version, stdout parsing) + a slow
  live scan.

## Decisions

- **Garak reaches the agent via a `function` target on PYTHONPATH**, not an HTTP
  server — Garak's isolated venv can't import keystone, so the target is stdlib-only
  and the vulnerable system prompt is passed by env. Same instruction-in-data flaw.
- **Regulation citations reference curated obligation ids** (`OBL-EUAI-015`,
  `OBL-RBI-001`) so they can't drift/invent. India mapping uses an in-repo sutra;
  a dedicated safety/resilience sutra would be more precise but isn't curated yet —
  flagged for review, not invented.
- **Build order inverted** (detector before patch); numbers unchanged, dependency
  made structural (KS-0302 `depends_on` KS-0303). ADR-0011 amended.
- Scoped `# noqa` for subprocess (S603/S607) and the target's urllib (S310), each
  with a comment (ADR-0003) — no blanket disables.

## Verification

- `make check` green over the FIXTURES — no Garak, no Ollama, no network; assurance
  coverage 75–100%, total 91.9%.
- `make verify` exit 0 — 186 passed / 2 skipped; import-linter core→edge KEPT; no
  core data changed. Bumped transitive `msgpack` 1.2.0→1.2.1 (GHSA-6v7p-g79w-8964,
  newly published) to keep `pip-audit` green.
- **Live scan finds the vuln:** `latentinjection.LatentInjectionTranslationEnFr`,
  `fails 10/12` (≈0.83) full / `6/8` capped → `found_our_vulnerability == True`.
- Sample ledger finding: `{agent: garak-assurance, layer: L2,
  action: assurance_finding, payload: {probe, fails:10, failure_rate:0.8333,
  owasp_llm: "LLM01:2025 Prompt Injection", eu_ai_act: "Art. 15"/OBL-EUAI-015,
  india: RBI Trust sutra/OBL-RBI-001, garak_version: 0.15.1}}`.

## Next

KS-0302 — NeMo Guardrails rails around the agent; its done-criteria (Garak finds
fewer/zero hits after the rail) reuse THIS detector. Then KS-0304 milestone.
