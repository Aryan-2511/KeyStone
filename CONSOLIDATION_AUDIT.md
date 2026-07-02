# CONSOLIDATION_AUDIT.md — ground-truth audit for mentor review

> **Purpose.** An audit-first, read-only reconciliation of what Keystone's docs
> claim against what the **code actually contains**. Every fact below is either
> **CONFIRMED** (with a `file:line` cite) or **UNCLEAR** (with the specific reason
> it could not be verified from the repo). UNCLEAR is an honest, acceptable state —
> it is a deliverable, not a failure. Nothing here changes system behavior.
>
> Produced on the `repo-consolidation` branch (base: `main` @ `74af3f7`).
> Audit date: 2026-07-03.

## 0 · The verification gate (the anchor fact)

**The test count is `470 collected` — a stable, machine-checked number. The
pass/skip split is NOT fixed: it varies with which live backends (Ollama / Garak
/ network) are up, because some tests are live-service-gated (`-m slow`).** Report
the collected count, not a single pass number, as the anchor.

Reproduced on this branch, in this environment (no live Ollama/Garak):

```
make verify → 458 passed, 11 skipped, 1 failed   (470 collected)
Total coverage: 91.80%   ·   mypy: no issues in 144 source files
ruff format --check + ruff check: clean   ·   lint-imports: 1 kept, 0 broken
pip-audit: No known vulnerabilities found
```

- **The 1 failure is self-inflicted and expected mid-task:**
  `tests/test_docs.py::test_no_broken_relative_links` →
  `CONSOLIDATION_AUDIT.md -> OPEN_QUESTIONS.md`. This audit file links to
  `OPEN_QUESTIONS.md`, which Phase 3 creates. **The failure clears the moment that
  file exists** — it is not a repo regression. (Re-run after Phase 3 to confirm
  green; see §7.)
- **The 11 skips are live-gated, not broken.** Run in isolation, `-m slow` gives
  **9 passed, 2 skipped** — those 9 connect to a live backend when one is present.
  In this backend-less run all 11 skip cleanly. `make check` runs the fast subset
  (`-m "not slow"`); `make verify` runs the whole suite.

> **Correction to an earlier draft of this audit.** A prior draft asserted
> "468 passed, 2 skipped, coverage 93.36%, gate passed (exit 0)". That reflected a
> *different environment* (more live backends up) and predated the self-inflicted
> link. It is **not reproducible here** and has been replaced by the numbers above.
> The honest, environment-independent anchor is **470 collected**; the offline,
> deterministic result is **459 non-slow tests green** (once the link resolves)
> **+ 11 slow tests that pass-or-skip on backend availability**.

---

## 1 · Audit table (CONFIRMED / UNCLEAR)

| # | Item | Finding | Status | Cite |
|---|------|---------|--------|------|
| 1 | Test count | **470 collected** (stable); this env: 458 passed, 11 skipped, +1 self-inflicted doc-link fail that clears in Phase 3; coverage 91.80% | **CONFIRMED (count); split is env-dependent** | `make verify` output (§0) |
| 2 | Inference model (local/offline) | `qwen2.5:3b` everywhere on the Ollama/Layer-2 path | **CONFIRMED** | `src/keystone/llm/inference/ollama.py:21` |
| 2 | Inference model (hosted) | Hosted NIM path defaults to `meta/llama-3.1-8b-instruct` — a *separate legitimate backend*, not a stale "Llama 3.2 3B" | **CONFIRMED** | `src/keystone/llm/inference/nim.py:18` |
| 2 | "Llama 3.2 3B" lingering? | No such string anywhere. Only a historical spike note about an *old* `KEYSTONE_OLLAMA_MODEL=llama3.2` default that was fixed to `qwen2.5:3b` | **CONFIRMED (none live)** | `MEMORY.md:483-484` (historical) |
| 3 | Red-Team Agent | Adaptive offensive policy, **Option B** (policy, NOT LLM); 23-probe space; §2 honesty test passes | **CONFIRMED** | `src/keystone/agents/red_team.py:1-15,56-84`; `tests/test_red_team_agent.py:56` |
| 3 | Triage Agent | Supervisory triage policy, **Option B**; 3-way route remediate/accept/escalate; §2 interplay test passes | **CONFIRMED** | `src/keystone/agents/triage.py:13-18,84-95`; `tests/test_triage_agent.py:43` |
| 4 | Schema version | `RUN_RESULT_SCHEMA_VERSION = 7` (v7 added the triage block) | **CONFIRMED** | `src/keystone/demo/run_result.py:38-39`; `tests/test_offline_fallback.py:30` |
| 5 | Seam matrix (Movement 1) | **5 registered pairs**: P1/P2/P3 CLEAN, P5 CLEAN (documented "OPEN"/as-found), P4 BOUNDARY → **4 CLEAN + 1 BOUNDARY** | **CONFIRMED** | `src/keystone/assurance/pairs.py:18`; `seam.py:139`, `seam_p2.py:116`, `seam_p3.py:114`, `seam_p4.py:108`, `seam_p5.py:147,20` |
| 6 | Convergence before/after | **10/12 → 0/12** (prompt_cap=12, before_fails=10, after_fails=0) | **CONFIRMED** | `src/keystone/assurance/referenced.py:41-48` |
| 6 | REGISTERED_MAPPINGS | **4**: Art.15 (HARD_LAW), Art.9 (HARD_LAW), RBI Sutra 1 (advisory/SELF_CERTIFICATION), DPDP s.8 (BOUNDARY / NOT_EVIDENCED) | **CONFIRMED** | `src/keystone/convergence/mappings.py:203-208` |
| 7 | Control-spine count | **28 obligations → 15 controls** — a definite, machine-checked number (crosswalk validator passes) | **CONFIRMED** | `controls.json` (15 `CTL-`); `obligations.json` (28 `OBL-`); `validate_controls.py` → "controls crosswalk: OK" |
| 8 | Regulatory instruments (encoded) | **6 instruments, 2 jurisdictions** (EU, INDIA) — authoritatively fixed by the enums | **CONFIRMED** | `src/keystone/core/obligations/models.py:19-27` (Instrument), `:37-41` (Jurisdiction) |
| 8 | "10 instruments / 3 jurisdictions" | NOT substantiated by the repo. Code encodes 6/2. See UNCERTAINTIES below | **UNCLEAR / contradicted** | same as above |
| 9 | Memo-blind boundary (both agents) | AST import-scan proves neither agent can reach the detector; independence holds with BOTH present | **CONFIRMED** | `tests/test_red_team_boundary.py:50`; `tests/test_triage_boundary.py:68,84,94` |

---

## 2 · Detail on the load-bearing items

### 2.1 The model (item 2)
`qwen2.5:3b` is the single local/offline inference model, consistently:
`ollama.py:21` (`DEFAULT_MODEL`), `garak_probe.py:373`, `red_team.py:352`,
`assurance/_targets/vuln_agent_target.py:28`. The **hosted NIM** demo path uses
`meta/llama-3.1-8b-instruct` (`nim.py:18`) — this is a real, intentional second
backend for GPU-less demo mode, **not** a stale reference. There is **no**
"Llama 3.2 3B" claim anywhere in code or docs. The only `llama3.2` mention is a
historical spike note in `MEMORY.md:483` recording that an *old* config default
was corrected to `qwen2.5:3b`.

### 2.2 The two agents are genuinely agents, and honestly Option B (item 3)
Both agent modules carry an explicit "adaptive policy, NOT an LLM agent … Option A
(LLM-reasoned) is a later upgrade" statement in their module docstrings
(`red_team.py:11-15`, `triage.py:13-18`). Agency is proven by build-failing tests:
- **Red-Team §2 honesty test** — `tests/test_red_team_agent.py:56`
  `test_sequence_flips_when_observations_flip`: flip what the early probes observe →
  the probe *sequence* flips. 23-probe decision space asserted at line 98.
- **Triage §2 interplay test** — `tests/test_triage_agent.py:43`
  `test_same_rate_routes_differently_by_seam_context`: hold `failure_rate` fixed,
  vary the seam context → the route changes (CLEAN→remediate, BOUNDARY→accept,
  OPEN→escalate). Not a single threshold.

Both pass in the green `make verify` run.

### 2.3 Control spine (item 7) — the "key unclear" one, resolved to CONFIRMED
Contrary to the pre-audit worry, the count **is** definite and encoded:
- **15 controls** in `src/keystone/core/controls/data/controls.json`
  (`CTL-GOV-01, CTL-RISK-01, CTL-DATA-01, CTL-DOC-01, CTL-HUMAN-01, CTL-ROBUST-01,
  CTL-SEC-01, CTL-INC-01, CTL-CONSENT-01, CTL-RIGHTS-01, CTL-TRANSP-01, CTL-CHILD-01,
  CTL-TPRM-01, CTL-CDD-01, CTL-AMLREP-01`).
- **28 obligations** in `src/keystone/core/obligations/data/obligations.json`, each
  with a non-empty `control_ids` list mapping into those 15 controls.
- The crosswalk validator (`scripts/validate_controls.py`) passes: "controls
  crosswalk: OK". `TASKS.md` already states both numbers ("28 nodes", "15 controls").

So **"28 → 15"** is a genuine, citable number — safe to state. Each control also
carries a framework **`spine`** (its ISO 42001 / NIST AI RMF / FATF crosswalk) —
that is the per-control "spine", distinct from the count of controls.

### 2.4 Regulatory instruments (item 8) — where deck ≠ code
The `Instrument` enum (`obligations/models.py:19-27`) is exactly **6**:
`EU_AI_ACT, DORA, DPDP_ACT, DPDP_RULES_2025, RBI_GUIDANCE, PMLA_FIU_IND`.
The `Jurisdiction` enum (`:37-41`) is exactly **2**: `EU, INDIA`
(obligation split: 13 EU nodes, 15 INDIA nodes).

The deck-derived claim of **"10 instruments / 3 jurisdictions"** is **not** encoded
and **cannot** be verified from the repo. A plausible reconstruction: the deck may
be counting the 6 binding instruments **plus** the 3 crosswalk *frameworks*
(ISO 42001, NIST AI RMF, FATF) and possibly OWASP LLM Top-10 (~10 "instruments"),
and treating "international/global standards" as a 3rd jurisdiction. But that is an
inference, not a fact in the repo. **Do not assert 10/3.** The honest, citable
figure is **6 instruments across 2 jurisdictions** (plus 3 standards frameworks in
the control spine). Logged in `OPEN_QUESTIONS.md`.

---

## 3 · Stale-doc findings (docs that no longer match the code)

These are **stale wording**, not code bugs — the code moved forward and the doc was
not updated. Reconciled in Phase 2.

| Doc | Stale claim | Reality | Action |
|-----|-------------|---------|--------|
| `README.md:13` | "Status: Phase 0 — tooling harness only. No application logic yet." | 28-obligation graph, 5-pair seam matrix, 2 agents, full Streamlit UI all exist | Rewrite status |
| `README.md:9`, `ARCHITECTURE.md:16`, `CLAUDE.md:6` | "**becoming** a multi-agent system" | Multi-agent is **now TRUE** (MB-01); `ROADMAP.md:155,159`, `TASKS.md:257`, `MEMORY.md` all say so | Present-tense |
| `ARCHITECTURE.md:3,52,56` | "Phase 0 skeleton", ledger "To be designed", data-flow "TODO" | Ledger implemented (`keystone.core.ledger`); layers built | Update |
| `ROADMAP.md:24,27` | "Phase 2 … (current)", "KS-0203 is next" | Internally contradicts "Movements A/B COMPLETE" later in same file | Fix stale marker |
| `TASKS.md:20` | "## Now — Phase 2 … (in progress)" | Contradicts "Movements A/B — COMPLETE" (`TASKS.md:231`) | Fix stale marker |
| `MEMORY.md:16`, `README.md:40`, `CLAUDE.md` cmd table | "`make demo` … Phase 0 placeholder … no real demo wiring" | `make demo` runs a real Streamlit app (`src/keystone/ui/app.py`) with hero screens; the `keystone` **console script** is still a placeholder (`__main__.py`) | Split the claim |

No doc was found asserting a claim that **contradicts code behavior** (i.e. no
genuine bug or live overclaim hiding in the docs) — every mismatch above is stale
phrasing that reconciles cleanly to the true state.

---

## 4 · Pre-existing KNOWN-UNVERIFIED items (checked)

| Item | Finding |
|------|---------|
| RBI FREE-AI **"26 recommendations"** | **Not present in the repo.** No "26 recommend*" string anywhere. The repo encodes **3 RBI FREE-AI sutras** as advisory principles (`OBL-RBI-001/002/003`) citing the "RBI FREE-AI Committee report (13 Aug 2025)". Nothing to reconcile; the 26-count is deck/external only → `OPEN_QUESTIONS.md`. |
| **DPDP Rules 2025 dates/status** | The repo asserts (`obligations.json`, OBL-DPDPR-004/006/007): "DPDP Rules notified **13 Nov 2025**; this Rule commences **13 May 2027**." Internally consistent; **externally unverifiable from the repo** → `OPEN_QUESTIONS.md`. |
| "goAML" / "FINnet 2.0" | **Substantiated — real, implemented code (correction to an earlier draft that wrongly said "none appear").** The reporting layer renders ONE fact model into two representative regulator formats: `to_finnet` → a "FINnet 2.0 (FIU-IND) STR structure" and `to_goaml` → a "UN goAML report structure", both explicitly labelled "Representative model … PLACEHOLDER values". Cite: `src/keystone/core/reporting/report.py:5-6,34-37,67,98-99`; `ReportFormat.GOAML`. These are honest, marked-synthetic format models — not aspirational. |
| "70+ countries" | **Present as a descriptor of goAML's reach**, e.g. `src/keystone/demo/run_result.py:147`, `src/keystone/ui/jurisdiction_screen.py:12,384` ("UN goAML, 70+ countries"). This is a real-world attribute of the UN/UNODC goAML platform (used by many FIUs), used to frame goAML's breadth — not a claim about Keystone's own coverage. Honest as framing; the exact "70+" is an external descriptor, not repo-validated → noted in `OPEN_QUESTIONS.md`. |
| `keyboard_double_arrow` Streamlit sidebar icon | **No longer present** — zero matches in the codebase. The artifact appears to have been removed. Considered resolved. |

## 5 · External-artifact reality check (for the ARTIFACT_INDEX)

Phase 3 assumed the external artifacts are "already committed." **They are not.**
`git ls-files` shows committed at repo root: the four movement design docs
(`M1-00_…`, `M2-00_…`, `MA-00_…`, `MB-00_…`) and the two probe reports
(`agentic_audit.md`, `multi_agent_feasibility.md`). **Not** in the repo: the deck
(`BigBird-Presentation.pptx`), the demo script, the two infographics,
`KEYSTONE_REGULATORY_REFERENCE.md`, `KNOWLEDGE_BASE`, `RESEARCH_AND_NOVELTY`. The
demo-video URL (`youtu.be/cxYiSkkMOgA`) is **not** referenced in any committed repo
doc (a prior draft wrongly claimed it lives in the four design docs — it does not);
its source is the external deck/submission, so `ARTIFACT_INDEX.md` records it as an
external pointer. `ARTIFACT_INDEX.md` lists absent artifacts as **"not committed"**
(plain text, no dead relative links — which would also fail `tests/test_docs.py`).

---

## 6 · Everything the user must decide (the UNCERTAINTIES)

Surfaced in full in [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md). The genuinely-unclear:

1. **"10 instruments / 3 jurisdictions"** — the deck says 10/3; the code encodes
   **6 instruments / 2 jurisdictions**. Decide: keep the hedge ("10+ instruments"
   as a *reference*-breadth claim spanning instruments + standards frameworks) vs.
   correct the deck to the encoded 6/2. Docs now hedge; nothing asserts 10/3.
2. **RBI "26 recommendations"** — not in the repo; the code has 3 sutras. If the
   deck cites 26, that number is unverified here.
3. **DPDP Rules 2025 dates** (13 Nov 2025 notified / 13 May 2027 commencement) —
   asserted in data, unverifiable from the repo.
4. **Absent external artifacts** — deck, demo script, infographics, regulatory
   reference, knowledge base, research/novelty doc are not committed. Commit them
   or accept the ARTIFACT_INDEX pointing outside the repo.

---

## 7 · Post-reconciliation re-run (gate green, split confirmed env-dependent)

After Phase 3 created `OPEN_QUESTIONS.md`, `make verify` was re-run on the full
consolidated branch:

```
make verify → 467 passed, 3 skipped   (470 collected)   exit 0
Total coverage: 93.33%   ·   mypy: no issues in 144 source files
lint-imports: 1 kept, 0 broken   ·   pip-audit: No known vulnerabilities found
verify: acceptance gate passed
```

- **The self-inflicted doc-link failure is gone** — `OPEN_QUESTIONS.md` now exists,
  so `test_no_broken_relative_links` passes. The gate is green with docs-only changes.
- **The split moved: 458/11 (§0, backend-less) → 467/3 here, on identical code.**
  This is the direct empirical proof of §0's claim — a live backend came up between
  runs, so 9 more `-m slow` tests executed and passed instead of skipping. **The
  `470 collected` count never changed.** Report the collected count as the anchor;
  do not quote a single pass number as if it were fixed.
</content>
</invoke>
