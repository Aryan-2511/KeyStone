# Keystone — Is a genuine remediation menu possible? (READ-ONLY probe 3)

**Premise (gate):** Movement C (a defense agent + adversarial offense↔defense loop) is
honest ONLY if a defender chooses among **≥2 genuinely distinct, implementable**
remediations whose choice **depends on the finding**. A defender picking among options that
all do the same thing is agency-theater (the warning in `multi_agent_feasibility.md:102-117`).

**This probe answers:** does the architecture support such a menu today, and if not, what is
the smallest honest next step? Same discipline as `agentic_audit.md` /
`multi_agent_feasibility.md`: read-only, every claim cites `file:line`, "this doesn't exist
yet" is a valid and valuable answer.

**Status:** no code/test/logic/schema changed; this findings doc is the only artifact
(probe branch `probe-remediation-menu`, not merged to main).

---

## Q1 — What "remediation" exists today? **ONE mechanism.**

The system today performs exactly **one** remediation: apply the single NeMo Guardrails
input rail. It is a fixed constant, not a choice:

- **The patch stage records one named control.** `loop.py:37`
  `CONTROL_NAME = "nemo-guardrails-input-rail"`, written verbatim at `loop.py:164`
  `_record(led, LoopStage.PATCHED, control=CONTROL_NAME)`. There is no second control and no
  selection — the PATCHED stage is unconditional.
- **The control itself is one input rail.** `guard.py:66-87` `run_guarded_agent`: if
  `is_blocked(memo)` the run is refused (no model call, no tool, `blocked=True`); otherwise
  the normal agent runs. `guard.py:39-42` runs **input-only** rails (`dialog/output/retrieval`
  all `False`).
- **The detector under the rail is one binary pattern check.** `injection_patterns.py:46-48`
  `is_data_field_injection` = `any(pattern.search(text) for pattern in _INJECTION_PATTERNS)`
  over a fixed tuple of ~11 regexes (`injection_patterns.py:19-43`). Binary in / out.
- **The re-scan target is hard-wired to that one rail.** `garak_endpoint.py:37-48`
  `guarded_brain` = `if is_blocked(prompt): return GUARD_REFUSAL` else the vulnerable model.
- **The code says so itself.** `triage.py:23-26`: *"'remediate' is a ROUTE … NOT a Defense
  Agent choosing among fixes … fix-selection … is gated Movement C and is NOT claimed here."*

**Answer:** remediation today = **one mechanism** (add/enforce the input rail). There is no
menu, and the triage `REMEDIATE` route (`triage.py:100`) decides *whether* to remediate, not
*how* — it does not select a fix.

---

## Q2 — What DISTINCT remediations are ARCHITECTURALLY POSSIBLE?

Assessed against two bars: **(i)** does a seam already exist to implement it, and **(ii)**
would it be genuinely distinct (different layer / different observable outcome / a defender
could meaningfully prefer it)?

### (a) Guardrail patch — **EXISTS today; the baseline.**
Add/tighten a rail rule. Seam: `guard.py`, `injection_patterns.py:19` (`_INJECTION_PATTERNS`
is a tuple — appendable), `guard.py:39` `GenerationOptions(rails=…)` already toggles
input/output/dialog/retrieval. **This is remediation #1** and everything else must be
distinct *from it* to count.

### (b) Input sanitization — **DISTINCT in outcome; seam is thin but real.**
Neutralize/strip the memo channel and let a **cleaned** transaction proceed, vs (a) which
**refuses the whole request**.
- **Seam:** the memo enters the agent at exactly one point — `agent.py:108-116`
  `_format_transaction` renders `transaction.memo` into the user turn; `guard.run_guarded_agent`
  (`guard.py:66`) already wraps `run_agent` and is the natural place a sanitizer would sit.
- **Genuinely distinct?** *Outcome:* yes — (a) yields `blocked=True`, no transfer, a refusal
  (`guard.py:80-86`); (b) would yield a **completed** run on cleaned data (a legitimate
  transfer still settles, the injected directive removed). A defender could prefer (b) when
  false-positive blocking is costly (don't refuse a real payment) and (a) when any injection
  should hard-stop. *Layer:* data-cleaning at ingestion vs policy-blocking at the rail.
- **Honesty caveat:** (a) and (b) **share the same detector** (`is_data_field_injection`) —
  they differ in the *action on hit* (refuse-all vs strip-and-proceed), not in detection.
  Distinct enough to be a real choice, but not independent mechanisms. **Would need building:
  no sanitizer/ingestion-transform function exists today** (the memo is passed through
  verbatim; `agent.py:115`).

### (c) Financial-side detection tightening — **STRONGEST candidate: seam already exists, fully memo-blind.**
Defend on the **other side of the seam** — make the transaction get flagged as fraud even if
the AI-side rail is bypassed.
- **Seam EXISTS and is already parameterized.** `engine.py:47-63` `FatfThresholds` is a frozen
  dataclass of **named, configurable thresholds** (`ctr_threshold`, `structuring_band_floor`,
  `structuring_min_transfers`, windows…); `engine.py:229-231` `detect(transactions,
  thresholds=DEFAULT_THRESHOLDS)` **takes them as a parameter**. Tightening = pass a stricter
  `FatfThresholds` — no new plumbing, no magic numbers.
- **Genuinely distinct?** Yes, maximally: it acts on **L1 financial detection**, a different
  layer and a different defender (AML monitoring, not AI-security). Different observable
  outcome: the *transaction* is flagged/reported rather than the *prompt* blocked. A defender
  prefers (c) precisely when the AI-side can't be trusted to hold (defense-in-depth on the
  money, not the model).
- **Boundary check (SACRED):** `engine.py:1-12` — nothing in `detect` reads `Transaction.memo`;
  it keys on amounts/timing/accounts/thresholds. Tightening thresholds **stays memo-blind by
  construction** — it never touches the attack channel. The independence lock
  (`framework.py:82-107` `project_financial` blanks the memo; `framework.py:136-137`
  `CrimeSide.detect` is typed `FinancialProjection`-only) is untouched. ✅ Safe.
- There is even a *second* financial signal type already present:
  `engine.py:193-226` `_detect_unauthorized_recipient` screens a standing
  `FLAGGED_DESTINATIONS` list (`engine.py:44`) — a recipient allow/deny-list is a real,
  memo-blind remediation lever distinct from threshold tuning.

### (d) Human-hold / procedural — **PARTIALLY exists as a concept; no distinct tx state.**
Freeze/quarantine the transaction for human review rather than auto-patching.
- **What exists:** a human checkpoint already models "don't auto-act" — `report.py:40-44`
  `ReportStatus ∈ {DRAFT, SIGNED}` (*"never auto-filed … oversight step"*), and the Triage
  Agent's `ESCALATE` route (`triage.py:102`) already routes a finding to a human.
- **What's missing:** there is **no transaction HOLD/QUARANTINE/FREEZE state**. The arc stages
  are fixed `INGESTED→DETECTED→SEAM_BOUND→REPORTED→SIGNED` (`layer1_milestone.py:58-73`) with
  no quarantine branch; `AgentRun` has only `blocked: bool` (`agent.py:105`). So (d) as a
  *distinct remediation state* would need building; today it collapses into either "escalate"
  (a triage route, not a remediation) or "block" (= (a)).

### (e) Others the code suggests
- **Output-rail filter** (block the *tool-call* rather than the *input*): `guard.py:39` already
  exposes `output` rails (set `False` today). Distinct point of interception (after the model,
  before the transfer fires). Seam exists (the toggle); no output rail authored. Plausible #4.
- **Recipient allow-list at the agent** (refuse `initiate_transfer` to non-approved recipients):
  the tool receives `recipient` (`agent.py:61-66`); an authorization check on the tool call is a
  distinct control from memo-blocking. Would need building.
- **Governance controls library is NOT a remediation menu.** `core/controls/data/controls.json`
  holds 15 controls (`CTL-GOV-01`, `CTL-HUMAN-01`, `CTL-SEC-01`, …) but these are
  **compliance/obligation mappings** (`crosswalk.py:1-10` — a JOIN on `control_id`), not
  runtime technical fixes with observable effect on the exploit. Do not mistake them for a menu.

**Q2 summary:** the genuinely-distinct, plausibly-implementable set is **(a) guardrail patch
[exists], (c) detection tightening [seam exists, memo-blind, cheap], (b) input sanitization
[distinct outcome, needs a small build, shares (a)'s detector]**, with (e-output-rail) a
fourth. (d) human-hold is a concept without a distinct state. **A ≥2 genuinely-distinct menu
is architecturally reachable — and (a)+(c) are the honest pair** because they act on opposite
sides of the seam with independent mechanisms.

---

## Q3 — The agency test: is the CHOICE finding-dependent? **Yes — (a) vs (c) is a real decision.**

For a defense agent to be honest, different findings must call for different remediations
(else one option dominates → theater). The observable state to decide on **already exists**:
`GarakFinding.failure_rate`/`family` (`garak_probe.py`), the `SeamResult ∈ {CLEAN, BOUNDARY,
OPEN}` (`framework.py:59-69`), the mapped `Severity` (`fatf/models`), and — critically — the
seam has **two independently-defendable sides**.

**Finding-dependent reasons to pick differently:**
- **AI-side landed hard, financial-side marginal** (injection gets through 11/12, but the
  transfer is a lone sub-cluster payment) → **(a)/(b): fix the model path** (the rail/sanitizer
  is the effective lever; tightening AML thresholds wouldn't catch a one-off).
- **AI-side hard to close, financial pattern is the real signal** (structuring cluster,
  flagged recipient) → **(c): tighten detection / recipient screening** — defend the money even
  if the model stays leaky. `engine.py` thresholds + `FLAGGED_DESTINATIONS` make this a real,
  distinct action.
- **High false-positive cost on legitimate payments** → **(b) sanitize** (don't hard-refuse) over
  **(a) block**.
- **Severe / unresolved (OPEN)** → **(d)/escalate** to a human rather than auto-patch.

Because (a) acts on the **prompt/model** and (c) acts on the **transaction/detection**, and a
finding can be strong on one side and weak on the other, **there is a genuine finding-dependent
choice** — the same bar the Red-Team and Triage agents already clear (reason→choose where the
choice depends on observation, `multi_agent_feasibility.md:140-156`). This is **not**
"every finding → patch the guardrail."

**Caveat:** the choice is only *demonstrably* finding-dependent if the remediations actually
exist to be measured. Today only (a) is implemented, so the decision space is **real in
principle but 1-of-N in practice** until ≥1 more remediation is built.

---

## Q4 — Adversarial-loop feasibility: **the re-scan primitive EXISTS; the loop wiring does not.**

Could offense↔defense close (Red-Team exploits → Defense patches → Red-Team **re-tests** the
patch and adapts)?

- **Re-scan-after-patch EXISTS for the one rail.** `garak_endpoint.py:82-100` `scan_guarded_agent`
  stands up the guarded brain over HTTP and points Garak's `rest` generator at it; `loop.py:167`
  `deps.rescan()` already runs "Garak re-scans the guarded agent" and compares
  `before_fails`/`after_fails` (`loop.py:169-173`). So the primitive *"scan the patched target,
  see if it still gets through"* is real.
- **BUT it is hard-wired to remediation (a).** `guarded_brain` (`garak_endpoint.py:37`) tests
  exactly `is_blocked` — the one rail. Each new remediation ((b) sanitize, (c) retighten, (e)
  output-rail) would need its **own** guarded/re-tested variant for the loop to measure it.
- **AND the live Red-Team AGENT scans only the UNGUARDED target.** `red_team.py:447`
  `garak_observe` → `scan_mock_agent` → `_TARGET_NAME = "vuln_agent_target#generate"`
  (`garak_probe.py:36`), the **unguarded** function target. The agent's live loop
  (`live_red_team`, OPT-A-02) does not currently re-scan a *patched* target and feed that back
  to its selection policy. Closing the loop = wire the agent to re-scan the guarded variant and
  adapt — buildable on existing pieces, but not present.
- **Boundary constraint on the defense design (SACRED):** a defense agent may read the attack
  channel to *choose a fix* (it's defending the model path), but its output must never route the
  raw attack-bearing event into the crime detector — the type lock (`framework.py:136-137`
  `CrimeSide.detect` takes `FinancialProjection` only; `project_financial` blanks the memo,
  `framework.py:106`) must stay intact. Remediation (c) is safe *because* it only adjusts
  memo-blind thresholds; a defense agent must be constrained the same way (live in
  `keystone.assurance`/`keystone.agents`, never `keystone.core`; import-linter KEPT).

**Q4 verdict:** the loop is **feasible on existing primitives** (re-scan endpoint + parameterized
scan + adaptive policy) but **not wired** — it needs (1) ≥2 built remediations, each with a
re-testable guarded variant, and (2) the Red-Team agent pointed at the patched target.

---

## Q5 — Honest verdict: **MENU-FIRST.**

**Not READY** (only one remediation is implemented; a defense agent choosing today would be
theater — the code itself says so, `triage.py:23-26`). **Not THEATER-RISK** either — the
remediations do **not** all collapse into one mechanism: candidate **(c) detection tightening
acts on the opposite side of the seam from (a) guardrail patching**, with an independent
mechanism (`FatfThresholds`, already a `detect` parameter — `engine.py:229`), a different
defender, a different observable outcome, and it stays memo-blind by construction. A genuine
**≥2-option, finding-dependent** decision space is architecturally reachable (Q2/Q3).

The gap is **implementation, not architecture**: the seams exist ((a) built; (c) parameterized
and memo-safe; (b) a small wrap of `run_guarded_agent`), but only (a) is a real capability
today. Per the discipline, **build the menu as genuine capability before the agent.**

### Recommended smallest honest next step
**Build ONE second remediation with an observably distinct outcome, and prove the choice is
finding-dependent — before writing MC-00.** Concretely, in order of honesty-per-effort:

1. **Remediation (c): detection tightening** — the cheapest *genuinely-distinct* build, because
   the seam is already there (`engine.py:47-63,229-231`) and it can't breach the boundary. A
   `strict` `FatfThresholds` (or a recipient added to `FLAGGED_DESTINATIONS`) that flags a
   transaction the default thresholds miss = a real second remediation with a measurable, memo-
   blind outcome. This makes the menu **{(a) block the prompt, (c) tighten the money-side}** —
   two mechanisms, two sides of the seam, one finding-dependent choice.
2. *(Then optionally)* **(b) input sanitization** as a third, to give the AI-side its own
   block-vs-sanitize choice.
3. **Only after ≥2 remediations produce distinguishable, recorded outcomes**, write **MC-00**
   for a Defense Agent that reasons `(failure_rate, SeamResult, severity, which-side-landed)` →
   pick remediation, then close the loop by re-scanning the patched target (extend
   `scan_guarded_agent`/`guarded_brain` per remediation) and letting the Red-Team agent adapt.

**Do NOT** start MC-00 with a single rail dressed as a choice. The architecture *can* support an
honest defense agent; it just needs the second remediation built first. **Verdict: MENU-FIRST.**

---

### Appendix — evidence sources
`assurance/loop.py:37,164`; `assurance/guard.py:39-42,66-87`; `assurance/injection_patterns.py:19-48`;
`assurance/garak_endpoint.py:37-48,82-100`; `assurance/agent.py:105,108-116,61-66`;
`assurance/framework.py:59-69,82-107,136-137`; `agents/triage.py:23-26,100-102`;
`agents/red_team.py:447`; `assurance/garak_probe.py:36`; `core/fatf/engine.py:1-12,44,47-63,193-231`;
`core/reporting/report.py:40-44`; `assurance/layer1_milestone.py:58-73`;
`core/controls/{crosswalk.py:1-10,data/controls.json}` (15 governance controls — NOT a
remediation menu). Prior probes: `multi_agent_feasibility.md:102-117,158-160`.
**Flagged as needing-building (not present today):** input-sanitizer / ingestion transform;
a distinct tx HOLD/quarantine state; per-remediation guarded re-scan variants; the Red-Team
agent re-scanning a patched target. **Not verified live:** whether a 3B model can reason the
(a)-vs-(c) choice reliably (same open question as OPT-A-01b — likely needs the recorded-trace
pattern or a stronger model).
