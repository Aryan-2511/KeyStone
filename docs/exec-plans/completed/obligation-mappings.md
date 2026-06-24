# Exec-plan: M2-02 — the rigorous obligation mappings (the convergence claim, populated)

- **Slug:** `obligation-mappings`
- **Feature IDs:** KS-0608 (M2-02) — done; unblocks KS-0609 (M2-0n the convergence result/UI)
- **Status:** done
- **Started:** 2026-06-24
- **Owner (session):** agent (Claude)

## Goal & acceptance

Populate the real evidence relationships through the M2-01 model: the seam event → named
obligations across EU hard law + India advisory, each clearing the four-part bar with a
defensible reason grounded in the actual control text, satisfy/violate DERIVED — plus the
DPDP boundary obligation (NOT_EVIDENCED by fund movement). Content + rigor, not new
architecture. Acceptance = KS-0608 `done_criteria`: the set clears the four-part bar with
real L3 refs; the cross-jurisdiction modality spread is present and real per-obligation;
the DPDP boundary is a principled NOT_EVIDENCED.

## Context / constraints

- NO new model architecture (M2-01 is the model). If a mapping needs the model to change →
  STOP, surface. NO UI/schema. NO touching M1 / the matrix / L3 obligations.
- Each `reason` must be specific + grounded in real text — a strained mapping is the
  checklist-RegTech failure; drop/surface rather than force.
- Boundary as principled as P4; modality real per-obligation; states DERIVED (inherited).

## Plan

- [x] Recon the real obligations/controls for each §4 mapping (summaries + control spine).
- [x] `convergence.mappings`: generic `_evidenced` / `_boundary` builders; build_reference
      (Art.15), build_risk_management (Art.9), build_rbi_trust (RBI), build_dpdp_boundary;
      `REGISTERED_MAPPINGS` set (mirrors REGISTERED_PAIRS). Export from `__init__`.
- [x] `tests/test_obligation_mappings.py` (four-part bar; real-L3 refs; modality spread;
      ISO/NIST via spine; DERIVED states; DPDP boundary principled).
- [x] Verify: `make check && make verify` green.
- [x] Docs: MEMORY / TASKS / ROADMAP / feature_list (KS-0608 done, KS-0609 planned).

## Progress log

- 2026-06-24 recon: real obligation summaries + control spine for the §4 set.
- 2026-06-24 built REGISTERED_MAPPINGS (3 EVIDENCED + 1 BOUNDARY); all refs resolve to
  real L3; modality spread 2 hard-law + 1 advisory.
- 2026-06-24 `make verify` green: 396 passed, 2 skipped; mypy strict / Ruff / import-linter
  clean, no new ignores. L3 / M1 untouched.

## Decisions

- **ISO 42001 + NIST AI RMF are evidenced VIA the control spine of real obligations, not as
  standalone obligations.** They are the control library's `Framework` enum (the spine
  every `CTL-*` maps to), NOT L3 obligations. Inventing them as obligations would violate
  "every ref resolves to a real L3 obligation"; treating them as a new bindable target
  would change the M2-01 model (a stop condition). So the §4 "ISO 42001" and "NIST" rows
  are honoured through the obligations whose controls crosswalk to them — Art. 9
  (CTL-RISK-01 → ISO 6.1/8.2 + NIST MAP/MANAGE = the input-manipulation risk-treatment +
  semantic-threat-modeling framings) and Art. 15 (CTL-ROBUST-01 → ISO 8 + NIST MEASURE) —
  with the framework clauses surfaced in each mapping's `requirement`. Honest + faithful;
  no model change.
- **The set is narrow-and-deep:** 3 EVIDENCED (Art.15 + Art.9 hard law EU, RBI Sutra 1
  advisory India) + 1 BOUNDARY (DPDP s.8). Modality spread real per-obligation.

## Open questions / blockers

- None. Each reason was written to be defensible against the real obligation text (the
  rigor a green gate can't check — see the PR report's quoted reasons).

## Next steps (resume here)

M2-0n / KS-0609 — the convergence result + UI: surface the loop (seam event → these named
obligations, violated→satisfied, EU + India + the DPDP boundary) as a figure/hero derived
from `REGISTERED_MAPPINGS`, honestly framed (`EVIDENCE_DISCLAIMER`). Likely a RunResult
schema bump (a convergence block) + a screen hosted in the shell with an AppTest gate — the
M1-06 schema+UI lessons apply (migrate every fixture; components.v1.html; ship the AppTest).

## Handoff (fill in on completion)

- **Changed:** `convergence.mappings` (+`_evidenced`/`_boundary` builders, the Art.9 / RBI
  mappings, the DPDP boundary, `REGISTERED_MAPPINGS`); package `__init__` exports; new
  `tests/test_obligation_mappings.py`; docs (MEMORY / TASKS / ROADMAP / feature_list KS-0608
  done + KS-0609).
- **Verified:** `make verify` green — 396 passed / 2 skipped; lint + mypy strict +
  import-linter clean, no new ignores. **L3 / M1 / the M2-01 model untouched.**
- **Deferred:** the convergence result/UI (M2-0n).
- **Recommended next task:** M2-0n / KS-0609 (the convergence result + UI).
