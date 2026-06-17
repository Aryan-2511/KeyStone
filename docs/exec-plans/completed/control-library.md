<!--
Exec-plan. Keep it current AS YOU WORK — handoff for any future session.
On completion run the verify gate and move to docs/exec-plans/completed/.
-->

# Exec-plan: Control library + obligations→controls crosswalk (KS-0202)

- **Slug:** `control-library`
- **Feature IDs:** KS-0202 (Phase 2 / Layer 3). Builds on KS-0201 (obligations +
  ADR-0012 schema) and is the Option-A control library ADR-0012 §5 reserved.
- **Status:** done (archived 2026-06-18)
- **Started:** 2026-06-18
- **Owner (session):** agent
- **Branched from:** `main` @ f8b6264 (merged KS-0201/0205; `make verify` green).

## Goal & acceptance

Build the shared control library (own data file, Option A), populate
`control_ids` on the 28 obligations, expose the crosswalk as a LOOKUP
(control→[obligations], modality-preserving), and ship the §5b fail-loud
referential-integrity validator.

- **`done_criteria` (KS-0202):** obligations map deterministically/reproducibly
  onto the shared control library (ISO/IEC 42001 + FATF + NIST AI RMF) with
  duplicate controls collapsed. **PLUS the §5b criterion this task owes** (added
  to feature_list per ADR-0012): every non-empty `control_id` resolves to a real
  control; an unresolved reference fails the build.
- **QUALITY.md:** #1 tests · #3 scope · #4 mypy strict · #5 ruff/S · #6
  architecture (deterministic core; no edge import) · #7 docs · #8 synthetic.

## Context / constraints

- ADR-0012 §5 Option A: control library is its own data file; obligations
  reference controls by `control_id`. §5a `control_ids` was optional in KS-0201;
  §5b: KS-0202 ships the fail-loud referential-integrity validator.
- Mirror `keystone.core.obligations` (model + fail-loud loader + JSON data) and
  `scripts/validate_obligations.py` (the §5b validator is its sibling).
- Deterministic core; import-linter (ADR-0008) forbids LLM-edge imports.
- **Control count is an OUTPUT, not a target.** Natural granularity; defensible
  to a domain expert; never force-merge to shrink. 1:1 allowed.

## Design (control count = 15, an output of honest grouping)

CTL- prefix convention: `CTL-<DOMAIN>-<NN>` (pattern `^CTL-[A-Z]+-\d{2}$`).
Spine = ISO/IEC 42001 + FATF + NIST AI RMF (each control maps to ≥1).

| Control | Obligations | Modalities |
| --- | --- | --- |
| CTL-GOV-01 Governance & accountability | DORA-005, DPDPA-008, DPDPA-010, RBI-001, RBI-002 | HARD+SELF |
| CTL-RISK-01 Risk management framework | EUAI-009, DORA-006 | HARD |
| CTL-DATA-01 Data governance & quality | EUAI-010, DPDPA-008 | HARD |
| CTL-DOC-01 Documentation & logging | EUAI-011, EUAI-012 | HARD |
| CTL-HUMAN-01 Human oversight | EUAI-014 | HARD (1:1) |
| CTL-ROBUST-01 Accuracy/robustness/resilience testing | EUAI-015, DORA-024 | HARD |
| CTL-SEC-01 Information security safeguards | DPDPA-008, DPDPR-006 | HARD |
| CTL-INC-01 Incident & breach mgmt/notification | DORA-017, DORA-019, DPDPA-008, DPDPR-007 | HARD |
| CTL-CONSENT-01 Notice & consent | DPDPA-005, DPDPA-006, DPDPR-004 | HARD |
| CTL-RIGHTS-01 Data-principal rights | DPDPA-011 | HARD (1:1) |
| CTL-TRANSP-01 Transparency & explainability | EUAI-013, RBI-003 | HARD+SELF |
| CTL-CHILD-01 Children's data protection | DPDPA-009 | HARD (1:1) |
| CTL-TPRM-01 Third-party risk | DORA-028 | HARD (1:1) |
| CTL-CDD-01 Customer due diligence (KYC) | PMLA-012, PMLA-009 | HARD |
| CTL-AMLREP-01 Transaction records & STR/CTR reporting | PMLA-012, PMLA-008 | HARD |

Judgment calls to flag: `DPDPA-008` (s.8 "general obligations") is a portmanteau
section → 4 controls (governance/data/security/incident) — honest multi-map, not
force-merge. `RBI-001` (Trust) → governance (foundational ethos). 4 genuine 1:1
controls (HUMAN/RIGHTS/CHILD/TPRM) — distinct domains, not merged.

## Plan

- [x] `src/keystone/core/controls/`: `models.py` (Framework enum, SpineMapping,
      Control), `loader.py` (fail-loud), `data/controls.json` (15), `__init__.py`.
- [x] `crosswalk.py`: `build_crosswalk(controls, obligations) -> list[ControlMapping]`
      by LOOKUP on `control_ids`; preserves `enforcement_modality` (modalities set).
- [x] Populated `control_ids` on the 28 obligations (data edit only; schema +
      citations untouched — surgical per-id regex on the `control_ids` line).
- [x] `scripts/validate_controls.py` (§5b): every `control_id` resolves; no
      orphan control; every obligation covered → hard errors. Wired into
      `make verify` + ci.yml (like the citation gate).
- [x] Tests (`tests/test_controls.py`): loader fail-loud; §5b real passes +
      dangling/coverage/orphan fixtures rejected; crosswalk no-orphan/coverage/
      both-modalities/deterministic; `@milestone` stable grouping. feature_list
      KS-0202 updated (+§5b criterion, status done, tests).
- [x] Break-it check (dangling ref → `make verify` exit non-zero, reverted);
      `make verify` green; TASKS/MEMORY/this plan updated.

## Progress log

- 2026-06-18 created plan. Branched `ks-0202-control-library` from green main
  f8b6264. Grouping designed (15 controls). Building now.
- 2026-06-18 implemented controls module (model/loader/data/crosswalk/__init__),
  populated control_ids on all 28 obligations, shipped §5b validator wired into
  make verify + ci.yml, added tests. `make verify` green (84 passed, 1 skipped,
  cov 92%). Break-it check confirmed non-zero exit + precise message; reverted.

## Decisions

- Control id convention `CTL-<DOMAIN>-<NN>`; count = output (15, not a target);
  modality preserved through crosswalk; §5b ships here. No new ADR — implements
  ADR-0012 §5/§5b. See [[MEMORY.md]].

## Open questions / blockers

- None blocking. Judgment calls for reviewer: `DPDPA-008` (s.8 portmanteau) maps
  to 4 controls; `RBI-001` (Trust) → governance; 4 genuine 1:1 controls.

## Next steps (resume here)

KS-0202 done. Next: **KS-0203** (EU hard-law vs India self-certification modality
contrast) — reads `ControlMapping.modalities`, already populated/preserved here.
Then KS-0204 (LLM-edge summary phrasing).

## Handoff

- **What changed:** new `src/keystone/core/controls/` (models, loader,
  data/controls.json [15], crosswalk, __init__); `control_ids` populated on the
  28 obligations (citations/schema untouched); `scripts/validate_controls.py`
  (§5b) wired into `make verify` + ci.yml; `tests/test_controls.py`; feature_list
  KS-0202 → done (+ §5b criterion, tests); TASKS.md + MEMORY.md updated.
- **Verified:** `make verify` exit 0 — 84 passed, 1 skipped, mypy strict + ruff
  (incl. S) + import-linter clean, coverage 92%. Break-it check passed.
- **Crosswalk result:** 28 obligations → **15 controls**, no orphans, full
  coverage; CTL-GOV-01 and CTL-TRANSP-01 expose BOTH modalities.
- **Deferred:** KS-0203 (modality contrast), KS-0204 (LLM-edge phrasing).
- **Recommended next task:** KS-0203.
