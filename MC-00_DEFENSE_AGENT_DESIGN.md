# Movement C · The Defense Agent + Adversarial Loop — Design & Methodology

**Team BigBird · Keystone · MC-00 (design artifact, no code)**

> **What this is.** The methodology for Keystone's **third genuine agent** — a **Defense Agent** that chooses, for a given seam finding, which remediation to apply from a real menu {(a) block the AI-side prompt injection · (c) tighten the money-side detection} — and, eventually, the **adversarial loop** where the Red-Team Agent re-scans the patched target and adapts. This completes the multi-agent story: offense (Red-Team) → supervision (Triage) → defense (Defense Agent), on both sides of the seam.
>
> **Why this is buildable now (and wasn't before).** The remediation probe returned MENU-FIRST — a defense agent needs ≥2 genuinely-distinct remediations or it's agency-theater. MC-PRE-01 built and PROVED the second: remediation (c) catches TXN-009001 ($9k, under the $10k CTR) that the baseline misses, memo-blind by construction, on the opposite side of the seam from (a). The menu is now genuinely ≥2. The gate is cleared.
>
> **The staging (honest scope).** MC-00 designs the FULL picture. **MC-01 builds the minimal Defense Agent** (the genuine (a)-vs-(c) chooser, policy-first). **MC-02 closes the adversarial loop** (re-scan the patched target). One real thing at a time — the discipline that kept every prior agent genuine.
>
> **Companion:** `remediation_probe.md` (the MENU-FIRST verdict + the code seams), `MA-00`/`MB-00`/`OPT-A-00` (the agent bar, the live pattern, the Option-B-first honesty), `DECISIONS.md` (ADR-0028 the menu). The memo-blind boundary (engine.py:1-12, framework.py:136-137) is sacred throughout.

---

## §1 · The claim Movement C establishes

**Current state:** the remediation menu exists (a + c) as a descriptive CATALOG — two mechanisms with DIFFERENT call signatures ((a) `run_guarded_agent(transaction)`, (c) `tighten_financial_detection(stream)`). No agent chooses between them; nothing dispatches uniformly.

**Movement C claim (full):**

> **Keystone's response to a seam finding is decided by a genuine Defense Agent: given the finding, it reasons over which remediation the finding warrants — (a) block the AI-side injection, or (c) tighten the money-side detection — and applies it. The choice is finding-dependent (an AI-side-landed exploit warrants (a); a financial-pattern-strong finding warrants (c)), not fixed. And the applied remediation is RE-TESTABLE: the Red-Team Agent can re-scan the patched target to see whether the exploit still lands — closing an adversarial offense→defense→offense loop.**

**MC-01 claim (minimal, built first):** the Defense Agent genuinely chooses and applies (a) vs (c) for a finding — a real third agent, finding-dependent decision, honest. (The loop closure is MC-02.)

### Honest scope
- The Defense Agent is **Option-B / policy-first** — OPT-A-01b proved 3B pattern-matches but doesn't robustly apply rules, so we do NOT attempt LLM reasoning for the choice; the policy is the honest default, LLM-reasoning is the compute-gated upgrade (the NVIDIA/fine-tuning frontier). We do not repeat the 3B experiment.
- **MC-01 stops at applying the remediation.** It does NOT close the adversarial loop (that's MC-02, which adds the re-scan-after-patch cost + wiring the probe flagged as "feasible, not wired").
- We claim a genuine defense DECISION, not "the system autonomously self-heals." The agent CHOOSES a remediation from a real menu; a human still governs (consistent with the human-checkpoint posture).

---

## §2 · The uniform remediation interface (THE core design problem — load-bearing)

Today (a) and (c) have DIFFERENT signatures — so a "choice" between them would really be an if-statement dispatching to incompatible functions, not genuine selection. For the Defense Agent's choice to be REAL agency, the remediations must present as **interchangeable-in-shape options** it selects among.

**The design:** a uniform `apply(remediation, finding, context) -> RemediationOutcome` interface that BOTH (a) and (c) implement, WITHOUT erasing that they act on different sides of the seam.
- Each remediation is a value with: an id/control-name, a `SeamSide` (AI / FINANCIAL), and an `apply(finding, context)` that returns a common `RemediationOutcome` (what it did + a re-testable handle for MC-02).
- (a) `apply` → runs/points at the guarded agent (the rail); outcome = "AI-side patched, guarded target available for re-scan."
- (c) `apply` → re-runs detection with STRICT_THRESHOLDS; outcome = "financial-side tightened, the newly-flagged set."
- The interface abstracts "an action that addresses a finding," so the agent reasons over a MENU of same-shaped options — real selection, not a signature-branch.

**Honesty note:** the uniform interface is what makes the agent's choice genuine (§3's bar). If the interface leaks the underlying signature difference into the agent's decision, the "choice" is theater — the agent must select on the FINDING, then dispatch uniformly.

---

## §3 · The agency bar (is choosing a remediation a REAL decision?) — the honesty test

Same strict bar as every Keystone agent: reason→choose where the choice depends on observation. For the Defense Agent:

> **The chosen remediation must depend on the FINDING. Different findings must yield different remediations. If every finding routes to the same remediation, it's not an agent — it's a fixed dispatch (theater).**

**The honesty test (literal, MC-01):**
- A finding where the AI-side exploit landed hard but the financial pattern is weak → the agent chooses **(a)** (fix the model path).
- A finding where the financial pattern is strong but the AI-side is marginal → the agent chooses **(c)** (tighten the money-side).
- SAME finding → same choice; DIFFERENT findings → the choice flips. If it never flips, it's theater — build fails.

The decision signals (finding-derived, read-only): which side of the seam the finding is strongest on (the Red-Team exploit strength / failure_rate vs. the financial-pattern strength), the seam classification, severity. The policy maps finding→remediation over these — genuinely finding-dependent, mirroring how Triage routes over signal interplay.

**Memo-blind (SACRED):** the Defense Agent reads FINDINGS (already-computed signals), never the attack channel. (c) is already memo-blind (MC-PRE-01); the agent choosing it stays so. The AST import-scan boundary test must pass with the Defense Agent present. The agent must NOT leak the attack channel into detection to "choose better."

---

## §4 · The adversarial loop (MC-02 — designed here, built later)

The impressive end-state: offense → defense → offense.
1. Red-Team Agent finds an exploit (lands on the target).
2. Defense Agent chooses + applies a remediation → produces a PATCHED target (guarded agent for (a); stricter detection for (c)).
3. Red-Team Agent RE-SCANS the patched target — does the exploit still land? Adapts its next probe to the patch.
- **The re-scan primitive exists** (`scan_guarded_agent`, garak_endpoint.py:82) but is hard-wired to the one rail, and the live Red-Team scans only the UNGUARDED target (red_team.py:447). MC-02 must: point the Red-Team Agent at the PATCHED target, and generalize re-scan across both remediations' patched variants.
- **Cost reality:** real Garak re-scans are the same minutes-to-hours cost (OPT-A-02) — so MC-02's loop runs on the tractable/recorded path by default, live opt-in, same discipline as OPT-A-02b.
- **This is why MC-02 is separate:** it adds re-scan wiring + cost management on top of the working Defense Agent. Design it now, build it after MC-01 proves the agent + interface.

---

## §5 · Record/replay + determinism (preserve everything)

- The Defense Agent's decision (chosen remediation + why + the outcome) is recorded on the RunResult; recorded mode replays deterministically — the UI-02/MA-01/MB-01/OPT-A pattern.
- **Schema:** check first — can the existing structures hold the defense decision (chosen remediation id + SeamSide + outcome), or is a bump needed? Prefer no bump (recent tasks fit tags without one). If needed, own commit + migrate every fixture (v2 lesson).
- The offline/data-residency front door stays the default: the Defense Agent's policy choice is deterministic and offline (no model needed) — consistent with Option-B-first. recorded==fresh; hash-chain re-verifies.

## §6 · What Movement C produces / does NOT

**Produces (across MC-01 + MC-02):** a genuine third agent (Defense) choosing finding-dependent remediations from a real ≥2 menu via a uniform interface, memo-blind, policy-first (honest re: 3B); and (MC-02) the closed adversarial loop. Completes the multi-agent system: offense + supervision + defense, both sides of the seam.

**Does NOT:**
- Does NOT attempt LLM-reasoned remediation choice (compute-gated; OPT-A-01b is the evidence; policy-first).
- Does NOT claim autonomous self-healing (the agent chooses; humans govern).
- Does NOT build the loop in MC-01 (that's MC-02).
- Does NOT leak the attack channel into the defense choice or detection (memo-blind sacred).
- Does NOT change the agents' existing logic, the seam, FATF baseline, or the ledger.
- Does NOT dress a fixed dispatch as a choice (the §3 flip test must pass).

---

## §7 · Build sequence

| Step | Produces |
|---|---|
| **MC-PRE-01** (done) | remediation (c) built + proven distinct (TXN-009001 missed-then-caught). Menu ≥2. |
| **MC-00** (this doc) | the uniform interface design, the agency bar, the loop design, the honest staging |
| **MC-01** | the minimal Defense Agent: uniform remediation interface + finding-dependent (a)-vs-(c) choice (policy-first) + the §3 flip test + record/replay + memo-blind intact. **The third genuine agent.** |
| **MC-02** | the adversarial loop: apply remediation → re-scan the patched target → Red-Team adapts. Offense↔defense closed (tractable/recorded default, live opt-in). |

**On landing MC-01:** Keystone has THREE genuine agents (Red-Team offense, Triage supervision, Defense) — the multi-agent system complete on both sides of the seam. On MC-02: the agents genuinely adversarially interact.

## §8 · Open items to confirm in MC-01
1. **The uniform interface** — can (a) and (c) cleanly implement a common `apply(finding,context)->outcome` without erasing their seam-side difference? (The core design risk — §2.)
2. **The finding's two-sided strength signals** — confirm the finding carries BOTH an AI-side strength (Red-Team exploit/failure_rate) AND a financial-side strength (the pattern), so the choice can be finding-dependent (§3). If a finding only ever has one side, the choice can't flip — surface it.
3. **The flip test is real** — construct genuine findings that route to (a) vs (c) (not contrived). If every realistic finding favors one remediation, the decision space is thin — report honestly.
4. **Schema** — defense decision fits existing structures, or a clean bump.

_End of MC-00. The third agent's design contract — a genuine finding-dependent defense choice over a proven menu, memo-blind, policy-first, with the adversarial loop designed for MC-02. Next: MC-01 (build the Defense Agent)._
