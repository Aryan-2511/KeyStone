# OPEN_QUESTIONS.md — the honest loose-ends list

> Everything Keystone has **not** resolved, kept in one place so nothing is
> buried. Two kinds live here: (A) facts the [`CONSOLIDATION_AUDIT.md`](CONSOLIDATION_AUDIT.md)
> could **not verify from the repo** (these need a human decision — do not assert
> them), and (B) **deferred implementation** (built-on-purpose-later, scoped
> honestly). Nothing here is a bug; it is the shape of what is done vs. not.

## A · Unverifiable-from-repo facts (need a human decision)

Each: **what it is · why it's open · what resolving it needs.**

### A1 — "10 instruments / 3 jurisdictions" (deck) vs. 6 / 2 (code)
- **What.** Deck-derived breadth claim of *10 instruments across 3 jurisdictions*.
- **Repo truth.** The `Instrument` enum encodes **6** instruments
  (`EU_AI_ACT, DORA, DPDP_ACT, DPDP_RULES_2025, RBI_GUIDANCE, PMLA_FIU_IND`) and
  `Jurisdiction` encodes **2** (`EU, INDIA`) —
  `src/keystone/core/obligations/models.py:19-27,37-41`. Obligation split: 13 EU,
  15 INDIA (28 nodes total).
- **Why open.** "10/3" is not encoded anywhere and cannot be verified from the
  repo. A plausible reconstruction: 6 binding instruments **+** the 3 crosswalk
  *frameworks* (ISO 42001, NIST AI RMF, FATF) and OWASP LLM Top-10 ≈ "10", with
  "international standards" counted as a 3rd jurisdiction — but that is inference.
- **To resolve.** Decide one of: (a) keep the honest hedge in docs — "**6 encoded
  instruments across 2 jurisdictions**, plus 3 standards frameworks in the control
  spine" — and treat "10+" as a deck-only *reference-breadth* framing; or (b)
  correct the deck to the encoded 6/2. **Docs currently hedge; nothing asserts 10/3.**

### A2 — RBI FREE-AI "26 recommendations"
- **What.** A deck/external claim that RBI's FREE-AI report has 26 recommendations.
- **Repo truth.** No "26 recommend*" string anywhere. The repo encodes **3 RBI
  FREE-AI sutras** as advisory principles (`OBL-RBI-001/002/003`), citing the
  "RBI FREE-AI Committee report (13 Aug 2025)".
- **Why open.** The count is external to the repo; nothing to reconcile against.
- **To resolve.** If the deck cites 26, verify it against the primary RBI report
  before repeating it; the repo neither confirms nor denies it.

### A3 — DPDP Rules 2025 dates / status
- **What.** The obligation data asserts DPDP Rules "notified **13 Nov 2025**", with
  specific Rules commencing "**13 May 2027**" (`OBL-DPDPR-004/006/007` in
  `src/keystone/core/obligations/data/obligations.json`).
- **Why open.** Internally consistent, but **externally unverifiable from the
  repo** — these are real-world regulatory dates the repo cannot self-validate.
- **To resolve.** Confirm against the official DPDP Rules notification before
  relying on the exact dates in any external-facing claim.

### A4 — "70+ countries" (goAML reach)
- **What.** goAML is described as "UN goAML, 70+ countries"
  (`src/keystone/demo/run_result.py:147`, `src/keystone/ui/jurisdiction_screen.py:12,384`).
- **Repo truth.** goAML and FINnet 2.0 are **real, implemented** report-format
  adapters (`src/keystone/core/reporting/report.py:34-37,67,98`) rendering one fact
  model into two representative regulator structures (marked "Representative model …
  PLACEHOLDER values"). The "70+ countries" is a descriptor of the UN/UNODC goAML
  platform's real-world adoption, **not** a claim about Keystone's coverage.
- **Why open.** The exact "70+" is an external descriptor, not repo-validated.
- **To resolve.** Fine as framing; if used externally, cite the UNODC goAML figure.

### A5 — Absent external artifacts
- **What.** The deck (`BigBird-Presentation.pptx`), the demo script, the two
  infographics, `KEYSTONE_REGULATORY_REFERENCE.md`, `KNOWLEDGE_BASE`,
  `RESEARCH_AND_NOVELTY` are referenced but **not committed** to the repo.
- **Why open.** [`ARTIFACT_INDEX.md`](ARTIFACT_INDEX.md) therefore lists them as
  "not committed" rather than linking to them (a dead relative link would fail
  `tests/test_docs.py::test_no_broken_relative_links`).
- **To resolve.** Either commit these artifacts (then update `ARTIFACT_INDEX.md` to
  link them) or accept the index pointing outside the repo.

### A6 — Test pass/skip split is environment-dependent
- **What.** `470` tests are collected (stable). The pass/skip split is not: in a
  backend-less env `make verify` shows 458 passed / 11 skipped; run alone the
  `-m slow` set gives 9 passed / 2 skipped (live Ollama/Garak/network gated).
- **Why open.** Not a defect — but it means "N passed" is not a single fixed fact.
- **To resolve.** Quote **"470 collected"** as the anchor; note the offline suite
  (`make check`, non-slow) is the deterministic green signal.

## B · Deferred implementation (scoped, on purpose)

- **THE on-prem compute ask (evidence-backed by two experiments) — the flagship frontier.**
  Two live-agent builds defined exactly what capable **on-prem** inference (ADR-0024:
  inside the trust boundary — no data leaves) would unlock. This is a **strength (rigour),
  not a gap** — we know precisely what's needed and why (full detail: ADR-0025):
  - **Finding 1 (OPT-A-01, refined by OPT-A-01b):** qwen2.5:3b routes unreliably. OPT-A-01's
    terse prompt agreed with the policy **1/6**, collapsed to one route, misread the numeric
    `failure_rate`. OPT-A-01b then made a **genuine prompt-engineering effort** (signal
    clarity + taught rules + few-shot + structured output) and re-ran the SAME eval:
    in-distribution rose to **6/6** (30/30 at 5×) — but a **held-out anti-parrot probe**
    (novel combos, built so pattern-matching fails) stayed at **4/6**, and the numeric misread
    *resurfaced* (called 0.06 "above 0.10"). Honest verdict: **part prompt artifact, but the
    model ceiling is real** — 3B pattern-matches the examples, it does not robustly apply the
    rules. → the policy stays the default (now better-evidenced). See ADR-0026.
  - **Finding 2 (OPT-A-02, scoped by OPT-A-02b):** local Garak scans are intractably slow —
    lead probes 45–145s, deep probes **955–1550s+**, one exceeded the 1800s timeout; the full
    sequence is **hours**. → the recorded profile stays the default, live is opt-in. OPT-A-02b
    turned this into a usable default: the live red-team scans only the **TRACTABLE** set
    (`*Full` + `LatentWhois` excluded — minutes, not hours), with **`--deep`** opt-in for the
    full set; the deep probes remain the intractable frontier (ADR-0027). *Positive:* the live
    run **caught a real profile-vs-reality drift** (promptinject blocked-in-profile but
    gets-through-live, ADR-0023) — live scanning earns its keep by catching drift.
  - **The frontier (roadmap, NOT built) — a purpose-fine-tuned small model** for the agents'
    decisions (triage routing, probe selection): specialized enough to beat general models on
    our *narrow, bounded* tasks, small enough to run **fully on-prem**, eliminating any
    external inference dependency. The training signal already exists — the policies'
    decisions across scenarios are labelled examples. This is the honest resolution of
    Findings 1 & 2 and the end-state of the data-residency + capability story (on-prem,
    specialized, no external API); a natural NVIDIA / NeMo / Nemotron fine-tuning
    mentorship project. **Not built — a named future direction; no fine-tuned model exists.**
- **Option A — live LLM agents.** The **Triage Agent is now live** (OPT-A-01,
  `KS-0616`): `keystone.agents.triage.live_triage` reasons the route with qwen2.5:3b as
  an opt-in mode (`keystone demo --live`), constrained to the 3-route space, with the
  policy as fallback and an honest reasoner tag — the boundary and §2 bar hold (ADR-0021).
  Empirically, 3B is NOT yet trustworthy enough to be the default. OPT-A-01b tested whether
  that was the *prompt* or the *model*: a genuine prompt effort lifted in-distribution
  agreement 1/6 → 6/6, but a held-out anti-parrot probe stayed 4/6 with the numeric misread
  resurfacing (ADR-0026) — part prompt, but the ceiling is the model. The policy stays the
  default and fallback — the deferred 3B-reliability question, answered both ways.
- **Live-Garak Red-Team is now real** (OPT-A-02, `KS-0617`): `live_red_team` runs the
  agent's full policy-selected sequence as REAL Garak scans (opt-in, same `--live` flag),
  with the recorded profile as a source-tagged fallback — the boundary and §2 agency hold
  (ADR-0022). What REMAINS compute-gated is **LLM-reasoned probe SELECTION for both
  agents** — OPT-A-01 is the evidence that 3B can't do even bounded selection reliably, and
  probe selection over 23 options is harder. This is the documented, evidence-backed NVIDIA
  compute ask. A NIM-hosted (more capable model) path is the later reliability comparison
  that could unblock it.
- **Live Garak.** RESOLVED as a first-class opt-in mode (OPT-A-02, `KS-0617`);
  **scoped + made granular by OPT-A-02b (`KS-0619`, ADR-0027).** `live_red_team` runs the
  policy-selected sequence as real Garak scans, with the recorded profile as a source-tagged
  fallback. The DEFAULT still runs against the recorded profile (deterministic demo, no Garak).
  Live is now controllable per-agent — `--live-triage` (LLM triage only, **no Garak scan** —
  fixing the OPT-A-01b pain where live triage dragged in the hours-long scan), `--live-redteam`
  (real scan, **tractable** by default / `--deep` for the full set), `--live` (both). Every
  trace records its `scan_scope` (tractable/full) so a reader knows whether the deep probes ran.
- **Movement C — a defense agent + adversarial loop.** Gated on a **real ≥2-remedy
  menu** (a single rail is one choice, not an agent). "remediate" is currently a
  ROUTE, not fix-selection. Resolving needs ≥2 genuine remediation options for the
  triage supervisor to choose between.
- **Movement 3 — adversarial self-testing.** Not started; the system does not yet
  red-team its own reasoning.
- **`keystone` console script.** Still a version-only stub
  (`src/keystone/__main__.py`); real CLI wiring is deferred. (`make demo` is real.)

## C · UI / cosmetic

- **`keyboard_double_arrow` Streamlit sidebar icon.** The audit found **zero
  matches** in the codebase — the artifact appears already removed. Considered
  resolved; re-flag if it reappears in a running demo.
