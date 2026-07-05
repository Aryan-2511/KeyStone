# MC-00 — Defense Agent design contract

> The design fixed BEFORE the code (generator/evaluator separation). Movement C makes
> Keystone a defense-capable multi-agent system: a third genuine agent that CHOOSES which
> remediation a finding warrants. This contract is the bar MC-01 is graded against.

## §0 — Premise & the gate that precedes the build

The remediation menu is now genuinely ≥2 (MC-PRE-01 / ADR-0028): **(a)** AI-side guardrail
block and **(c)** financial-side detection tightening, on opposite sides of the L2↔L1 seam.
A defender is honest only if the choice among them is **finding-dependent** — else it is a
fixed dispatch dressed as an agent (theater).

**The Phase-0 gate (MENU-FIRST discipline, applied to the DECISION).** Before building the
agent, MC-01 must PROVE — from real data — that findings carry **independent two-sided
strength** and that the choice can genuinely flip. If every realistic finding favours one
remediation (the strengths are always correlated, or one side dominates), STOP: the decision
space is thin and Movement C needs rethinking. Do NOT build a dispatch and call it an agent.

## §1 — What the agent is (and is NOT)

- **IS:** a supervisory **Defense Agent** that reads a finding's already-computed signals and
  chooses **(a)** or **(c)**, then applies the chosen remediation via a uniform interface.
- **IS policy-first:** the choice is a transparent policy, **NOT an LLM** — OPT-A-01b proved a
  3B model cannot reason a bounded choice reliably; LLM-reasoned remediation choice is
  compute-gated. Honest label: *"adaptive defense policy (finding-dependent remediation
  selection; not an LLM)."*
- **IS memo-blind:** it reads FINDINGS (signals) only — never the attack channel. It must not
  reach the memo/attack channel to "choose better." (c) stays memo-blind (re-runs the
  memo-blind engine); (a)'s rail may read the memo when APPLIED (the AI-side defense is
  allowed to — it is not the crime detector), but the agent's CHOICE never does.
- **IS NOT** an autonomous self-healer: the agent chooses; humans govern.
- **IS NOT** the adversarial loop: MC-01 STOPS at applying the remediation. Re-scan / close the
  offense↔defense loop is **MC-02** — the interface is built loop-ready, not wired.

## §2 — The uniform remediation interface

Both remediations implement one interface so the agent selects on the finding then dispatches
uniformly — never a signature-branch masquerading as a choice:

- `Remediation.apply(context) -> RemediationOutcome`, where `RemediationOutcome` carries: the
  `control` name, the `SeamSide` (AI / FINANCIAL), a `summary` of what it did, concrete
  `detail` (e.g. the tx ids (c) newly flags), a `retest_via` handle (for MC-02's loop), and
  `verified_offline` (True/False for (c) — verifiable now; **None** for (a) — its effect needs
  the MC-02 re-scan). The asymmetry is honest: (c) is a pure offline detection change (instantly
  verifiable); (a) is an AI-path control whose verification is a re-scan.
- The interface **abstracts "an action addressing a finding" without erasing the seam-side
  difference** (`side` is on every outcome). `context` carries what each apply needs (the tx
  stream for (c); the operative-tx handle for (a)) — the run context, not the agent's choice input.

## §3 — The policy (the finding-dependent choice)

Signals (memo-blind, already computed): **`failure_rate`** (AI-side strength — the Red-Team's
landed-exploit rate), **`financial_gap`** (financial-side — is there a transaction baseline
detection MISSES that STRICT_THRESHOLDS catches), plus `seam_result` and `severity` (recorded,
enrich the rationale). The choice is a function of the **two-sided strength**:

```
ai_live = failure_rate >= DEFENSE_FLOOR (0.10)
choose (c) FINANCIAL_TIGHTENING  iff  (financial_gap and not ai_live)
choose (a) GUARDRAIL_PATCH        otherwise
```

Both signals matter: (c) is reached only when the money is provably slipping detection AND the
injection is contained — the residual risk is money movement, so tighten the money-side.
Otherwise (a): the injection is live (close the AI hole — the root cause, upstream of the
transfer; correct even if the money-side also has a gap), or neither hole is open (harden the
input rail as the structural default — the memo channel is the vulnerability class).

Quadrants: strong-AI/weak-fin → (a); weak-AI/strong-fin → (c); both → (a) (root cause first);
neither → (a) (default hardening). (a) is the default/root-cause control; (c) is the specific
"money slipping while AI contained" control.

## §3 tests — the proof it is an agent, not a dispatch

1. **The flip test.** A strong-AI/weak-financial finding → (a); a weak-AI/strong-financial
   finding → (c). Same finding → same choice; the two findings produce DIFFERENT remediations.
   If the choice never flips, it is theater — fail.
2. **All-options-reachable.** Both (a) and (c) are genuinely chosen by some real finding
   (neither is dead) — mirrors the triage all-routes-reachable test.
3. **Same-finding determinism.** Same finding → same remediation (the policy is a pure function
   of the finding).

## §4 — Boundary & record/replay (sacred)

- **Memo-blind:** the agent reads signals only; the AST import-scan boundary test passes with
  the Defense Agent present; (c) stays memo-blind (a test pins detect(strict) blank == injected).
- **Record/replay:** the defense decision replays deterministically (the policy needs no model);
  the offline / data-residency default is intact. Schema: fit existing structures — add
  `defense` as an OPTIONAL defaulted field on `RunResult` (**no version bump**, mirroring
  OPT-A-01's `reasoner` / OPT-A-02's `source`); regenerate `recorded_run.json` (recorded==fresh);
  the hash chain re-verifies.

## §5 — Out of scope (explicit deferrals)

- **LLM-reasoned remediation choice** — compute-gated (OPT-A-01b); the policy is the honest
  default and the fallback shape a live mode would take.
- **The adversarial loop (MC-02)** — re-scan the patched target and let the Red-Team agent
  adapt; the uniform interface's `retest_via` handle is built for it, not wired here.
- **Additional remediations** ((b) input sanitization, output-rail, human-hold) — the menu is
  extensible; MC-01 ships the proven ≥2.
