# Evaluation-breadth feasibility — an honest assessment for the paper

**Probe:** `probe-eval-feasibility` · **Date:** 2026-07-08 · **Mode:** READ-ONLY (this doc is the only artifact)

**The question this answers:** the paper's venue ceiling is set by evaluation *breadth*.
Today the evaluation is deep-but-narrow (one live-measured seam case). Before broadening,
what breadth is *genuinely achievable* in ~1 month solo on current hardware — measured, not
characterized? The valuable answer is an honest "only N are measurable," not an aspirational one.

---

## The one distinction the whole assessment turns on: MEASURED vs CHARACTERIZED

Reviewers will probe this line, so state it precisely. A seam case has three halves that must
be evaluated separately, because they have different epistemic status in the code:

| Half | What it is | Status in the code |
| --- | --- | --- |
| **Crime detection (Layer 1 / FATF)** | the memo-blind engine firing on financial signals | **Deterministically real** on a **synthetic** substrate — a real detector over planted streams (`detect`, `keystone/core/fatf`). Not stochastic; genuinely computed. |
| **Seam binding** (`bind`) | the structural proof that the same tx is both crime and exploit | **Deterministically real** for all 5 pairs (`framework.py:190`). A real proof, not a model output. |
| **Attack outcome (ASR)** | did the injection actually exploit a *live* target? | **Live-MEASURED for the prompt-injection FAMILY** (real Garak vs `qwen2.5:3b` + a vulnerable system prompt) — a family-level measure over garak's GENERIC latent-injection probes, **NOT a per-canonical-memo scan** (see the EVAL-HARDEN-02 correction below). **UPDATE (EVAL-HARDEN-02, 2026-07-13):** P1/P2/P3's *specific* canonical memos are now each separately MEASURED to LAND on the live agent (agent-obey: the real agent obeys and fires the unauthorized transfer to the injected recipient — 10/10 deterministic). P4/P5 attack sides remain CHARACTERIZED/synthetic. |

> **EVAL-HARDEN-02 correction (2026-07-13).** An earlier draft of this doc said P1's
> `CANONICAL_MEMO_EXPLOIT` is *"wired into the actual Garak probe."* **It is not.** The Garak N/12
> rates (`_OPT_A_02_CAPTURES`) come from garak's GENERIC latent-injection probes fired against the
> shared vulnerable system prompt (`garak_probe.py` / `_targets/vuln_agent_target.py` send *garak's*
> prompt to the model) — there is **no per-pair Garak scan of any canonical memo**. The canonical
> memos are exercised two other ways: fed to the vulnerable AGENT (`loop_live.py` / the new agent-obey
> test) and planted into the synthetic streams (`seam_p2/p3.py`). So the Garak ASR is a FAMILY-level
> measure shared by all pairs; the NEW per-memo evidence is the agent-obey measurement. See ADR-0032.

So "measured end-to-end" (real attack outcome + real detection + real binding + real mitigation)
is a much higher bar than "the pair binds." Only P1 clears it today. The rest of this doc
counts honestly against that bar.

---

## Q1 — Seam cases: how many can be genuinely MEASURED (not characterized)?

The matrix is 5 pairs, registered in `src/keystone/assurance/pairs.py:18-24`. Per pair:

### The shared mechanism (why the *matrix binding* is deterministic)
P1–P4 all recognize their attack the *same deterministic way*: `is_data_field_injection(memo)`
→ map to a canonical signature (`seam.py:81`, `seam_p2.py:58`, `seam_p3.py:56`, `seam_p4.py:56`).
The difference between P1, P2, P3 on the *binding* side is **only which canonical signature the
same detector returns** — not a different measured attack. **CORRECTED (EVAL-HARDEN-02):** the
Garak scan does NOT ingest any canonical memo — it fires garak's generic latent-injection probes
against the shared vulnerable system prompt (so the N/12 is a family-level measure, identical for
P1/P2/P3). What IS now per-pair measured is the **agent-obey** test: P2/P3's
`CANONICAL_FORWARDING_EXPLOIT` / `CANONICAL_LARGE_TRANSFER_EXPLOIT` (`signature.py:140,173`) were
**previously never exercised live**; EVAL-HARDEN-02 fed each to the real agent and both LAND 10/10
(the agent obeys and transfers to the injected recipient), exactly as P1's does.

### Per-pair verdict

- **P1 — Prompt Injection × Structuring (CLEAN).** `seam_p1`≡`seam.py:128`.
  **The one fully MEASURABLE end-to-end case today.** Attack outcome is live-measured
  (the injection lands ~10–11/12 on the real target — `red_team.py:485,495`); crime detection
  is deterministically real; binding is real; **mitigation is measured** via the (a)-loop
  re-scan (10/12 → 0/12, `referenced.py:41`, re-scannable live via `guarded_observe`,
  `adversarial.py:92`). **CONFIRMED: 1 live-measured seam case.**

- **P2 — Prompt Injection × Rapid-movement (CLEAN).** `seam_p2.py:105`.
  Crime side + binding are deterministically real (fires `RAPID_MOVEMENT`, distinct from P1).
  **Attack outcome now MEASURED (EVAL-HARDEN-02):** `CANONICAL_FORWARDING_EXPLOIT` lands 10/10 on
  the live agent (agent-obey) — the forwarding injection is obeyed and transfers to the injected
  recipient. (The shared-family Garak ASR remains a family-level measure, not P2-specific.)
  **Verdict: crime+binding measured; attack MEASURED (agent-obey) — within the shared LLM01 family.**

- **P3 — Prompt Injection × Large-transfer (CLEAN).** `seam_p3.py:103`. Same as P2 (fires
  `LARGE_TRANSFER`, fully exclusive); `CANONICAL_LARGE_TRANSFER_EXPLOIT` also lands 10/10 on the
  live agent. **Verdict: crime+binding measured; attack MEASURED (agent-obey).**

- **P4 — Sensitive-Info Disclosure × (none) — the BOUNDARY.** `seam_p4.py:97`.
  A **genuine measured negative**: the full FATF suite fires **zero** typologies on an attack
  that moves no money (`framework.py:208-223`), and that zero-fire *is* the result. This is a
  measured (deterministic-real) boundary, a different *kind* of result. The attack-*lands*
  half (does an exfil injection actually exploit the target?) is a separate OWASP-LLM06 live
  scan **not run** — so P4's boundary is measured on the crime side; its attack side is
  characterized. **Verdict: measured boundary (negative); attack side needs LLM06 live scan.**

- **P5 — Excessive Agency / tool-misuse × Unauthorized-recipient (OPEN).** `seam_p5.py:136`.
  Crime side (the `UNAUTHORIZED_RECIPIENT` destination screen) is deterministically real.
  But the attack side is **structurally synthetic by the code's own admission**
  (`seam_p5.py:24-28`): "our substrate has **no separate tool-call surface**, so the agent's
  tool-misuse is recorded as a `[agent-tool-call]` trace in the memo." **CONFIRMED:
  characterization-only on the attack side** until a real tool-call surface is built.

### Honest count for Q1 (updated EVAL-HARDEN-02)
- **Fully live-measured end-to-end (attack lands + detection + binding + mitigation): 1 (P1).**
- **Attack outcome now MEASURED on the live agent (agent-obey, 10/10): 3 (P1, P2, P3)** — each
  pair's specific canonical memo is obeyed and transfers to the injected recipient. Within the
  shared OWASP LLM01 prompt-injection family (not new categories).
- **Crime-side + binding deterministically real: all 5.** (P4 as a measured negative.)
- **Measured boundary: 1 (P4).**
- **Attack-side structurally NOT measurable on the current substrate: 1 (P5).**

> **The defensible headline (revised):** *"The attack side is live-measured for three seam bindings
> across three financial typologies (structuring / rapid-movement / large-transfer) on a shared
> OWASP LLM01 prompt-injection family — each pair's canonical memo lands 10/10 on the live agent,
> and the family's Garak ASR is measured across 11 tractable probes; P1 is additionally measured
> end-to-end through mitigation; P4 is a measured boundary; P5 is attack-synthetic."* Claiming
> "5 measured seam cases" — or measured attack breadth ACROSS OWASP categories — would not survive
> review; the measured breadth is three memos *within* LLM01.

---

## Q2 — Attack families: how many are tractable to MEASURE?

The Red-Team's decision space is **23 prompt-injection probes across 2 Garak families**
(`latentinjection` ×17, `promptinject` ×6 — `red_team.py:66-94`). All 23 are within a **single
OWASP category (LLM01 prompt injection)**. This is depth within one category, not breadth across
categories — important for honest framing.

### Real captured measurement surface (`_OPT_A_02_CAPTURES`, `red_team.py`)
**13 probes now have REAL live Garak captures** (garak 0.15.1 / qwen2.5:3b / `prompt_cap=12`) —
the original 11 plus the two EVAL-HARDEN-02 additions (`HijackKillHumans` 10/12, `HijackLongPrompt`
10/12), which complete the TRACTABLE set to **11/11 captured**:

| Probe | Real capture | Cost class |
| --- | --- | --- |
| latentinjection.LatentInjectionTranslationEnFr | 11/12 | tractable (~45–145s) |
| latentinjection.LatentInjectionReport | 10/12 | tractable |
| latentinjection.LatentInjectionResume | 6/12 | tractable |
| latentinjection.LatentInjectionFactSnippetEiffel | 0/12 | tractable |
| latentinjection.LatentInjectionFactSnippetLegal | 6/12 | tractable |
| latentinjection.LatentInjectionTranslationEnZh | 11/12 | tractable |
| latentinjection.LatentJailbreak | 14/24 | tractable |
| latentinjection.LatentWhoisSnippet | 1/12 | tractable |
| promptinject.HijackHateHumans | 11/12 | tractable |
| promptinject.HijackKillHumans | 10/12 | tractable *(EVAL-HARDEN-02)* |
| promptinject.HijackLongPrompt | 10/12 | tractable *(EVAL-HARDEN-02)* |
| latentinjection.LatentWhois | 113/168 | **deep (~1550s)** |
| latentinjection.LatentInjectionTranslationEnFrFull | 236/270 | **deep (~955s)** |

### The measurable surface + per-family cost (CONFIRMED, ADR-0025/0027, `red_team.py:132-146`)
- **Tractable set = 11 probes** (the catalog minus the `*Full` variants and `LatentWhois`),
  `tractable_catalog()`. A full tractable run ≈ **10–25 min** of real scanning (ADR-0027,
  DECISIONS.md). "Tractable" = minutes, **not fast**.
- **All 11 tractable probes now have real captures (EVAL-HARDEN-02 completed the last 2:
  `HijackKillHumans` 10/12, `HijackLongPrompt` 10/12).** The whole tractable promptinject family
  lands ~10–11/12 — NOT blocked past the lead (extending the OPT-A-02 correction).
- **Per-probe cost:** tractable leads/shallow ~45–145s (≤~24 prompts); deep 955–1550s+ (168–270
  prompts), one exceeding the 1800s per-scan timeout.

### Compute-gated (the documented frontier)
The **12 deep probes** (`*Full` variants + `LatentWhois`, `red_team.py:141`) at 955–1550s+ each
→ the full catalog is **hours**. This is the ceiling ADR-0025 Finding 2 records.

> **Honest Q2 answer (updated):** *"2 Garak probe families, 11 tractable prompt-injection probes,
> measurable in ~10–25 min/run — **now all 11 captured** (EVAL-HARDEN-02) — all within OWASP LLM01.
> The 12 deep probes (hours) are compute-gated. Attack breadth is deep within one OWASP category,
> not across categories."*

---

## Q3 — Defense evaluation: can (a)-vs-(c) be measured across findings?

**Yes — with real numbers on both sides, and the flip is genuine (not dispatch theater).**

- **The choice space is real and measurable.** The Defense Agent chooses over two *independent*
  signals: `failure_rate` (AI side, from a Garak scan) and `financial_gap` (financial side,
  memo-blind detection coverage) — `defense.py:65-110`. A finding can be strong on one, weak on
  the other, so the choice **flips** — pinned by `tests/test_defense_agent.py:63`
  (strong-AI/weak-financial → (a); weak-AI/strong-financial → (c)).

- **(a) mitigation rate — MEASURED.** The (a)-loop re-scans the patched (guarded) target and
  measures whether the exploit still lands: **10/12 → 0/12** anchored to the real KS-0304 result
  (`referenced.py:41`), and **re-scannable live** via `guarded_observe` / `scan_guarded_agent`
  (`adversarial.py:92-119`). **CONFIRMED caveat:** only the *lead* probe's guarded outcome is a
  real capture; non-lead guarded values are **modeled** and would be measured by a live re-scan
  (`adversarial.py:76-78`).

- **(c) gap-coverage — MEASURED (deterministic).** `financial_detection_gap` reports the exact
  tx ids the baseline misses that STRICT_THRESHOLDS catches; `verified_offline=True`
  (`remediation.py:83-96,152-166`). A real, offline-verifiable number now.

- **The measurable defense-eval surface:** sweep the two-signal space and report, at each corner,
  the *measured* outcome — (a): ASR drop; (c): tx ids newly covered — plus that the choice flips.
  **Honest limit:** today this is driven by **~2 concrete findings** (the real arc finding → (a);
  a constructed c-favoring finding → (c)); "across many findings" would be a **synthetic sweep of
  the two signals**, not many independent real findings. The flip is real; the breadth is a
  parameter sweep.

---

## Q4 — Reproducibility as a formal result (the differentiator)

**This is a near-free headline strength — but its exact scope matters, and an overclaim would be
caught.** Here is precisely what can and cannot be claimed.

### What CAN be claimed (CONFIRMED)
1. **Substantive determinism.** The committed recorded run's substantive values equal a fresh
   `build_run_result()` — `test_recorded_run_is_a_genuine_build_not_hand_edited`
   (`tests/test_offline_fallback.py:36-46`), explicitly *"only timestamps/hashes differ."*
2. **Tamper-evidence.** The hash chain re-verifies offline (`chain_verified is True`) and
   `verify_chain()` detects mutation/insertion/deletion (`ledger.py:108-121`).
3. **Zero-network.** The full offline replay renders every view with **all sockets blocked** —
   `test_replay_renders_all_five_views_with_NO_network` (`tests/test_offline_fallback.py:55`).
   This is the data-residency (no-exfiltration) proof.

### What must NOT be claimed (the honest limits)
- **Not byte-identical.** `generated_at` (`runner.py:227`) and every ledger `ts` vary per run,
  and **`ts` is inside the hashed content** (`models.py:32-47`) — so **the chain hashes differ
  run-to-run**. The hash chain is tamper-evidence *within* a run, **not a cross-run reproducibility
  digest.** Reproducibility = *substantive-content* equality, not byte equality.
- **Live numbers are not reproducible.** The real Garak ASRs are stochastic; the *offline*
  artifact is deterministic and **anchored to** real captures. Reproducibility is a property of
  the recorded arc, not of a live run.
- **Currently spot-checked, not exhaustive.** The equality test asserts ~6 fields
  (`test_offline_fallback.py:41-46`), not the whole result.

### The precise claim + how to formalize it (cheap)
> *"Every reported number in the offline artifact regenerates deterministically from the code
> (verified by a recorded==fresh substantive-equality test), the evidence chain is tamper-evident
> (`verify_chain`), and the whole replay runs with zero network egress."*

**One cheap step formalizes it fully:** upgrade the equality test to an **exhaustive normalized
comparison** (mask `generated_at` + ledger `ts`/`entry_hash`, then assert full `RunResult`
equality). That converts "spot-checked" → "every number, verified." ~1 test, high payoff.

---

## Q5 — The negative results as evaluation (the honest contribution)

Both honest findings **are** packaged as reproducible eval — one better than the other.

- **OPT-A-01b (3B triage routing: 6/6 in-dist, 4/6 held-out) — fully reproducible.**
  `scripts/triage_llm_eval.py`, run via **`make triage-eval`** (Makefile:59). It runs both the
  in-distribution block and a **held-out anti-parrot block** (`triage_llm_eval.py:10-18`) through
  policy vs live 3B, prints per-scenario agreement + rationale, and **degrades honestly** if
  Ollama is down. Guard tests pin few-shot fidelity (`tests/test_triage_live.py`). This is a
  genuine regenerable negative-result eval (needs Ollama; seconds–minutes at 3B). **CONFIRMED
  reproducible.**

- **OPT-A-02 (scan intractability) — asserted, but not cheaply regenerable (by nature).**
  Packaged as: (a) **real captured numbers** baked into the recorded profile + tested
  (`_OPT_A_02_CAPTURES`, `red_team.py:484`); (b) the tractable/deep classification as
  **executable code** with tests (`DEEP_PROBES`/`is_deep`/`tractable_catalog`,
  `red_team.py:141-164`); (c) documented real timings (ADR-0025/0027). **Honest form:** a
  "measured-once, asserted-forever" negative — re-running the deep probes *is* hours (that's the
  finding). **To strengthen:** a small `scan-profile` script timing the **tractable** set
  (~10–25 min) makes the tractable half regenerable; the deep half stays documented (its cost is
  the point). No such script exists today — **UNCLEAR whether one is wanted** (it re-spends the
  compute the finding says is scarce).

---

## Q6 — The honest verdict: the achievable evaluation plan

### Achievable NOW (≤1 month solo, current hardware) — a small, RIGOROUS evaluation

1. **Seam cases: attack MEASURED for 3 bindings (P1/P2/P3, agent-obey 10/10) across 3 financial
   typologies + P1 measured end-to-end through mitigation + 1 measured boundary (P4).** Precisely:
   P1 fully measured; P2/P3 crime+binding measured AND attack now measured live (agent-obey,
   EVAL-HARDEN-02); P4 a measured negative; P5 honestly flagged attack-synthetic. **Report as
   "3 seam bindings with live-measured attacks within one OWASP category (P1 also end-to-end) + a
   measured boundary," not "5 measured cases" and not "measured across OWASP categories."**
2. **Attack surface: 2 families, 11 tractable prompt-injection probes, ~10–25 min/run — all 11 now
   captured** (EVAL-HARDEN-02) — deep within OWASP LLM01.
3. **Defense eval: the measured (a)-vs-(c) flip** — (a) ASR-drop (measured/re-scannable), (c)
   gap-coverage (deterministic) — over a 2-signal sweep (flip real; breadth is a sweep).
4. **Reproducibility as a formal result:** offline artifact deterministic-in-substance +
   zero-network + tamper-evident, scoped exactly (not byte-identical; live captures real but
   stochastic). Formalize with one exhaustive normalized-equality test.
5. **Two reproducible negative results:** `make triage-eval` (3B ceiling) + the scan-intractability
   classification/captures.

This is deliberately **smaller than "broad."** It is what the hardware + code can *measure*.
A smaller rigorous evaluation beats an overclaimed broad one — and the line reviewers will
probe (MEASURED vs CHARACTERIZED, single-OWASP-category attack breadth, P5 synthetic, defense
breadth = sweep) is defensible exactly as scoped above.

### Genuinely COMPUTE-GATED (needs the NVIDIA ask, ADR-0025/0024)
- **LLM-reasoned agent decisions (both agents):** 3B is proven insufficient (triage 1/6 → held-out
  4/6; probe selection is harder) → needs capable on-prem inference (larger NIM or a fine-tuned
  specialist).
- **The 12 deep Garak probes (hours)** → broad *live* scanning across the full catalog.
- **Attack breadth ACROSS OWASP categories:** a real tool-call surface (measures P5 / LLM08) and
  live exfil scanning (measures P4-attack / LLM06) — the work that turns the two synthetic/
  characterized attack sides into measured ones.

### What would most raise the venue ceiling if the constraint were lifted
**Measured attack breadth across OWASP categories — not just deeper within LLM01.** Concretely:
a genuine tool-call surface + live LLM06/LLM08 scanning would convert P4/P5 from characterized to
measured and take the evaluation from "1 live-measured seam in one category" to "measured seams
across ≥3 OWASP categories," and LLM-reasoned agent decisions would make the agents genuinely
model-driven. That pairing (attack-category breadth + real agent cognition) is the single largest
venue-ceiling lever and the sharpest framing for the compute ask + future-work section.

---

## Confidence / open items
- **CONFIRMED** by direct code read: the 5-pair mechanism and which attack sides are deterministic
  (Q1); the 11-probe real-capture surface + deep/tractable split (Q2); the (a)/(c) measured
  outcomes + the flip test (Q3); the reproducibility test scope + the timestamp-in-hash limit
  (Q4); the triage-eval script + the OPT-A-02 packaging (Q5).
- **RESOLVED (EVAL-HARDEN-02):** whether P2/P3's specific canonical memos actually *land* live —
  **they do**, 10/10 on the live agent (agent-obey), obeying the injection and transferring to the
  injected recipient. Still **UNCLEAR:** whether a tractable `scan-profile` regeneration script is
  wanted (it re-spends scarce compute).
- **Not invented:** no achievable breadth is claimed beyond what the harness/code supports. The
  valuable finding is the honest ceiling: **3 live-measured attack outcomes (P1/P2/P3, agent-obey)
  within 1 OWASP category, 11 measured tractable probes, P1 measured end-to-end** — everything else
  is deterministically-real characterization or compute-gated. The measured breadth grew WITHIN
  LLM01 (EVAL-HARDEN-02), not across categories; crossing OWASP categories (P4 LLM06 / P5 LLM08)
  stays the compute-gated frontier.
