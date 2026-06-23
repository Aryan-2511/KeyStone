# Exec-plan: M2-01 — the Evidence Model (seam event → obligation, satisfy/violate)

- **Slug:** `evidence-model`
- **Feature IDs:** KS-0607 (M2-01) — done; unblocks KS-0608 (M2-02 the obligation mappings)
- **Status:** done
- **Started:** 2026-06-24
- **Owner (session):** agent (Claude)

## Goal & acceptance

Movement 2's architectural core: a typed model binding a seam event to the regulatory
obligation(s) it evidences, carrying BOTH satisfy/violate states DERIVED from the real
before/after data, plus the M2-00 §2 four-part rigor as structure. Subsume the existing
L3 cleanly. NO mappings yet (one reference mapping only), NO UI. Acceptance = KS-0607
`done_criteria`: the reference mapping has all four parts and subsumes L3; the state is
DERIVED (change the numbers → it changes); reason mandatory; boundary representable;
"not lawyers" encoded; L3 stays green and unchanged.

## Context / constraints

- NO parallel obligation registry — reference the EXISTING `core.obligations` (stop cond).
- Satisfy/violate DERIVED from before/after, not a static flag (stop cond).
- Reason mandatory, enforced structurally (stop cond).
- Edge logic over L3 + the matrix; core unaware (import-linter KEPT). Don't touch M1.
- M2-00 §2 (rigor bar), §3 (satisfy/violate), §4 (obligations + boundary), §6 ("not lawyers").

## Plan

- [x] Step-0 L3 recon → `M2-00` §7a (obligation shape; before/after reachable; DPDP boundary).
- [x] New edge package `keystone.convergence` (added to import-linter forbidden-for-core).
- [x] `convergence.evidence`: `EvidenceState`, `EvidenceKind`, `derive_state`, `BeforeAfter`,
      `ObligationRef.from_obligation`, `SeamEventRef`, `EvidenceRelationship` (mandatory
      reason + EVIDENCED-needs-before_after validators; pre/post/transition derived props),
      `EVIDENCE_DISCLAIMER`.
- [x] `convergence.mappings`: the ONE reference mapping (P1 × OBL-EUAI-015 / CTL-ROBUST-01),
      built from real L3 + REFERENCED_ASSURANCE.
- [x] `tests/test_evidence_model.py` (four parts; subsumes L3; derived state /
      change-the-numbers; mandatory reason; boundary; not-lawyers).
- [x] Verify: `make check && make verify` green.
- [x] Docs: MEMORY / TASKS / ROADMAP / feature_list (KS-0607 done, KS-0608 planned) +
      `M2-00` §7a recon.

## Progress log

- 2026-06-24 recon: L3 obligation/control shape; REFERENCED_ASSURANCE reachable; DPDP
  obligations exist for the boundary. Reference mapping = EU Art. 15 (OBL-EUAI-015).
- 2026-06-24 built the evidence model + the one reference mapping; state derives
  VIOLATE→SATISFY from 10→0.
- 2026-06-24 `make verify` green: 389 passed, 2 skipped, 94.56% coverage; mypy strict /
  Ruff / import-linter clean (convergence on the edge), no new ignores. L3 untouched.

## Decisions

- **New `keystone.convergence` edge package** — `policy` is specifically NeMo Guardrails;
  convergence is a distinct Movement-2 concern. Added to the core's import-linter
  forbidden list (core can never import it).
- **State derivation is a pure function** (`derive_state(fails, exploit_fired)`) so the
  satisfy/violate state can't drift from the real numbers — proven by a change-the-numbers
  test. The relationship carries BOTH states + the transition (the M2-00 §3 contribution).
- **Boundary = `EvidenceKind.NOT_EVIDENCED`** (no before_after, no state, reason still
  mandatory) — mirrors M1's BOUNDARY; the §4 DPDP boundary slots in without special-casing
  (proven by a stub using a real DPDP obligation).
- **Reference mapping = EU Art. 15** (OBL-EUAI-015 → CTL-ROBUST-01, ISO 42001 Clause 8 +
  NIST MEASURE) — anchors both the "EU Art. 15" and "ISO 42001 robustness" framings in one.

## Open questions / blockers

- None blocking. For M2-02: the §4 set (ISO 42001 / NIST / RBI + the DPDP boundary), each
  clearing the four-part bar; confirm ISO/NIST exact clause numbering at the paper pass.

## Next steps (resume here)

M2-02 / KS-0608 — the rigorous obligation mappings. Add the §4 obligations through the
evidence model (ISO 42001, NIST AI RMF, RBI Sutra 1 OBL-RBI-001, + the DPDP data-protection
BOUNDARY evidenced only by P4). Narrow-and-deep — each clears the four-part bar with a
before/after state; the DPDP boundary is a principled NOT_EVIDENCED. Reuse the `convergence`
helpers (`_obligation_by_id`, `_control_by_id`, `_requirement_text`).

## Handoff (fill in on completion)

- **Changed:** new `keystone.convergence` (evidence model + one reference mapping);
  pyproject import-linter (+convergence forbidden-for-core); new `tests/test_evidence_model.py`;
  docs (MEMORY / TASKS / ROADMAP / feature_list KS-0607 done + KS-0608 / `M2-00` §7a).
- **Verified:** `make verify` green — 389 passed / 2 skipped / 94.56% cov; lint + mypy
  strict + import-linter clean, no new ignores. **L3 untouched; M1 untouched.**
- **Deferred:** the obligation mappings (M2-02) + the convergence result/UI (M2-0n).
- **Recommended next task:** M2-02 / KS-0608 (the rigorous obligation mappings + DPDP boundary).
