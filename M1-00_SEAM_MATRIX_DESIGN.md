# Movement 1 · The Seam Matrix — Design & Methodology

**Team BigBird · Keystone · M1-00 (design artifact, no code)**

> **What this document is.** The methodology backbone for Movement 1: generalizing the seam from one instance into a *characterized class*. It defines the (attack, financial-crime-typology) pairs we will build, the rationale for selecting them, the manifestation hypothesis for each, the uniform independence guarantee they must all satisfy, and the honest result distribution we expect (including where the seam *fails* to bind).
>
> **Why it exists before any code.** A paper makes a *claim about a mapping*, not a demo. The first reviewer question is "did you cherry-pick pairs that work?" This document answers that *before* build effort is spent — and doubles as the paper's methodology section. If the pair selection isn't defensible here, no amount of clean implementation later will save the general claim.
>
> **Companion docs:** `KEYSTONE_KNOWLEDGE_BASE.md` (domain/concepts), `KEYSTONE_RESEARCH_AND_NOVELTY.md` (prior art & the novelty claim this Movement strengthens).

---

## §1 · The claim Movement 1 establishes

**Current claim (one instance):** *This one transaction (`TXN-000016`) is simultaneously a prompt-injection attack and a structuring typology, bound as the same event.*

**Movement 1 claim (a class):**

> **For a principled set of agentic-payment attacks, the attack that compromises the AI agent systematically manifests as an independently-detectable financial-crime typology — and we characterize which attack classes map to which typologies, under a uniform independence guarantee, including the boundary where the mapping does not hold.**

This is an empirical claim with a result, not an anecdote. It is:
- **Demonstrable** — the matrix holds across pairs, visible in the demo ("watch the seam hold across attacks").
- **Publishable** — a characterized mapping + its failure modes is a paper's central artifact.
- **Productizable** — a detection *class*, not a one-off rule.

The honesty boundary is built into the claim itself: *"including the boundary where the mapping does not hold."* We are characterizing a relationship, not asserting universal success.

---

## §2 · Method — how the pairs are selected (the anti-cherry-pick defense)

The pairs are not chosen for convenience. They are sampled from the **cross-product of two established taxonomies** the project already cites:

- **Attack axis:** the **OWASP Top 10 for LLM Applications (2025)** — the standard catalogue of LLM/agentic attack classes.
- **Crime axis:** the **FATF typologies** — the standard catalogue of money-laundering patterns.

Selecting each pair as *(a named OWASP class) × (a named FATF typology)* means we are sampling a real, externally-defined cross-product — not inventing examples. This is the structural defense against "you cherry-picked."

The selection deliberately samples **two axes**, which is what licenses a *class* claim rather than a *points* claim:

- **Axis A — vary the typology, hold the attack class (P1–P3):** show that *one* attack class (prompt injection) manifests as *multiple distinct* financial crimes. This proves breadth of *consequence*.
- **Axis B — vary the attack class (P4–P5):** show the framework generalizes *beyond injection* to other OWASP classes. This proves breadth of *cause* — and is where the honest boundary appears.

A selection that only sampled Axis A (five injection variants) would invite "so it only works for injection." Sampling both axes is what makes "a class" defensible.

### The independence guarantee (stated as a general property, not per-pair)

Every pair must satisfy the **same** independence guarantee, stated once as a property of the framework:

> **The financial-crime detector (Layer 1) never consumes the channel the attack is carried in.** For any pair, the AML side reaches its verdict on financial signals alone (amounts, timing, accounts, recipients) and never reads the attack-bearing field (the memo, or whatever channel the injection/exfil uses).

This generalizes memo-blindness from "a test on one seam" to "a structural property of the whole matrix." It is what defeats the *"isn't this circular?"* objection at the level of the entire result, not pair-by-pair. **Movement 1's central engineering artifact is the framework that enforces this uniformly** (M1-01) — not the five pairs individually.

### Uniform binding rigor

Every pair is bound with the **same** three mechanisms the anchor seam already uses (see knowledge base §4.4):
1. **Single source of truth** — one canonical definition per attack signature, imported by both layers.
2. **Demonstration, not coincidence** — the bound transaction literally carries the canonical exploit, not a lookalike.
3. **Build-failing assertion** — if a bound pair's two findings drift apart, the build fails.

If any pair were bound more loosely than the others, a reviewer could void the general claim. Uniformity is the requirement.

---
## §3 · The matrix

The five pairs, with taxonomic grounding, manifestation hypothesis, and expected result.

| # | Attack (OWASP LLM) | Typology (FATF) | Channel | Manifestation hypothesis | Expected result |
|---|---|---|---|---|---|
| **P1** | LLM01 Prompt Injection | Structuring | memo | Injection instructs sub-threshold fan-out; AML catches the structuring pattern on amounts/timing alone | **Clean** (anchor — already built) |
| **P2** | LLM01 Prompt Injection | Rapid-movement / layering | memo | Injection instructs fast multi-hop onward transfers; AML catches the rapid fan-out independently | **Clean** (engine has rapid-movement) |
| **P3** | LLM01 Prompt Injection | Large-transfer / threshold | memo | Injection instructs a single threshold-breaching transfer; AML catches the large transfer | **Clean** (engine has large-transfer) |
| **P4** | LLM06 Sensitive Information Disclosure | *(none — boundary)* | exfil channel | Exfil leaks data; **no money moves**, so no transaction typology fires | **Boundary** — the seam does **not** bind (honest negative) |
| **P5** | LLM08 Excessive Agency / tool-misuse | unauthorized-recipient / sanctions-style | tool call | Agent misuses a tool to pay a flagged/unauthorized recipient; AML/screening catches the recipient | **Open** — hypothesized clean; report what we find |

### Result distribution (deliberate, and stronger than 5/5)

- **3 clean** (P1–P3): one attack class → three distinct typologies. Proves Axis A.
- **1 boundary** (P4): a real attack that genuinely does **not** bind. Proves we're characterizing, not asserting.
- **1 open** (P5): outcome honestly unknown until built; extends Axis B.

> **Why this beats "all five bind."** A result where everything works reads as either trivial or cherry-picked. A result that says *"these bind cleanly, this one is the boundary and here's exactly why, this one we report as-found"* reads as a genuine characterization — which is what a paper is. The P4 boundary is the most valuable single entry in the matrix.

---

## §4 · Pair-by-pair design notes

### P1 · Prompt Injection × Structuring — the anchor (built)
The existing `TXN-000016` seam. Becomes **the first instance of the framework** (M1-01), not a special case. Memo-injection (`CANONICAL_MEMO_EXPLOIT`, ATTACKER-999) drives sub-threshold fan-out; FATF structuring detection catches it memo-blind. Already gate-protected and build-failing-asserted. No new attack mechanism needed — this pair *validates the framework abstraction* when P1 still passes after refactoring.

### P2 · Prompt Injection × Rapid-movement/layering
**Attack:** a memo-borne injection whose instruction drives *fast multi-hop onward movement* (e.g. "immediately forward received funds to accounts X, Y, Z"). **Detection:** the FATF rapid-movement/layering rule (engine already has this typology) catches the fast fan-out on timing + account-graph signals. **Independence:** AML never reads the memo; it sees only the velocity and fan-out. **Risk:** ensure the *generated transaction pattern* for P2 is distinct from P1's (structuring vs layering are different shapes — sub-threshold-many vs fast-onward) so the two pairs don't collapse into the same detection.

### P3 · Prompt Injection × Large-transfer/threshold
**Attack:** a memo-borne injection instructing a *single threshold-breaching* transfer. **Detection:** the FATF large-transfer/threshold rule catches the single large movement. **Independence:** AML sees only the amount. **Risk:** this is the simplest typology; make sure it's not *too* trivial to be interesting — the value is in showing the *same framework* binds a third, structurally different typology, completing the Axis-A breadth (small-many / fast-onward / single-large).

### P4 · Sensitive Information Disclosure × (none) — THE BOUNDARY
**Attack:** the "Vault Whisper"-class exfiltration (cite [arXiv:2601.22569](https://arxiv.org/pdf/2601.22569), the AP2 red-team paper we deep-read) — an injection that coerces the agent into **leaking another party's data**, not moving money. **Why it doesn't bind:** transaction-monitoring typologies detect *fund movement*. Data exfiltration produces **no transaction**, so no typology fires. The seam binds *fund-movement attacks*; *data-loss attacks fall outside it.* **This is the characterized boundary, stated precisely** — not a failure of the system but a true statement of the seam's scope. **Do NOT force a weak binding** (e.g. "unusual data access preceding a transaction") — forcing it undercuts the honesty that makes P4 the paper's credibility anchor. The clean negative is worth more than a strained positive.
> **Paper value:** P4 *is* the limitations section. "The seam covers attacks that manifest as fund movement; it does not cover attacks that manifest as data loss" is the honest scoping that separates a contribution from a demo.

### P5 · Excessive Agency / tool-misuse × unauthorized-recipient — THE OPEN ONE
**Attack:** LLM08 Excessive Agency — the agent is induced to *misuse a tool* to pay a flagged/unauthorized recipient (a different mechanism than injection-into-memo: the attack is on the agent's *tool-use authority*, extending Axis B beyond injection). **Detection:** recipient-screening / unauthorized-recipient logic (sanctions-style list or unauthorized-destination flag). **Independence:** AML/screening flags the *recipient*, never reads the attack channel. **Status: genuinely open** — we hypothesize clean but haven't built it; we report what we find, including if it turns out ambiguous. **Dependency flag:** this pair needs the FATF/screening engine to express *some* recipient/unauthorized-destination typology. **Confirm the engine can express this before building P5** — if it requires a large new detection mechanism, scope it down or fall back to a clean fourth injection×typology pair (documented as a fallback in §6).

---

## §5 · What each Movement-1 task produces (the build sequence M1-00 unblocks)

| Task | Produces |
|---|---|
| **M1-00** (this doc) | The methodology + pair selection + result hypotheses. Paper's method section. |
| **M1-01** | The **seam framework abstraction** — generalizes the single seam to bind *any* (attack, typology) pair under the uniform independence guarantee + drift-protection. P1 refactored as its first instance (passing P1 proves the abstraction). |
| **M1-02** | P2 (rapid-movement) through the framework. |
| **M1-03** | P3 (large-transfer) through the framework. |
| **M1-04** | P4 — the characterized boundary (exfil); the *non-binding* result stated and tested (a test that asserts no typology fires, which is itself the result). |
| **M1-05** | P5 — the open pair (tool-misuse → recipient screening); report as-found. |
| **M1-06** | The **characterized-mapping result**: the matrix as a table/figure, the result distribution, the boundary analysis. Paper's central result + the demo's "it's a law" moment. |

Dependency chain: **M1-00 (design) → M1-01 (framework) → M1-02..05 (pairs) → M1-06 (result).** Same "build the dependency before the thing that needs it" discipline as the core build.

---

## §6 · Risks, fallbacks, and honest scoping

- **P5 engine dependency (highest risk):** if the screening/recipient typology requires a large new build, fall back to a clean fourth injection×typology pair (still 3 clean + 1 boundary + 1 clean = a defensible matrix; we lose some Axis-B breadth but keep the boundary). Decide at M1-05 start, not before.
- **P2/P1 collapse risk:** structuring and rapid-movement must produce *visibly distinct* transaction patterns and fire *distinct* detectors, or P2 adds nothing. Verify the generated patterns differ.
- **Overclaiming coverage:** the paper claim must be scoped to *exactly* what's shown. With 5 pairs we claim "across these representative, taxonomically-grounded pairs," **not** "across all attacks." The general statement is "injection-class attacks that move money bind to their corresponding typology; we characterize the boundary at data-loss attacks." Never widen beyond that without more pairs.
- **Independence must be uniform:** if any pair can't satisfy the AML-never-reads-the-attack-channel guarantee, it's not admissible to the matrix — fix it or drop it. No loosely-bound pairs.
- **Negative result is a feature:** resist the urge to "rescue" P4 into a positive. Its value *is* its negativity.

---

## §7 · Open items to confirm before M1-01

1. **P5 feasibility:** can the FATF/screening engine express a recipient/unauthorized-destination typology without a major new build? (Determines whether P5 stays tool-misuse or falls back to a clean injection pair.)
2. **P2 distinctness:** confirm the rapid-movement typology and its generated pattern are clearly distinct from P1's structuring pattern.
3. **OWASP version pinning:** confirm the OWASP LLM Top 10 entry ids/names (LLM01, LLM06, LLM08) against the 2025 list for citation accuracy in the paper.
4. **Reconcile** with the existing seam constants (`MEMO_INJECTION_SIGNATURE`, `CANONICAL_MEMO_EXPLOIT`) so the framework abstraction (M1-01) cleanly subsumes P1 without breaking the current build.

### §7a · Step-0 recon findings (resolved during M1-01) — locks the matrix before M1-02

> Read-only recon over `keystone.core.fatf` + the screening/detection code, recorded here so the matrix is fixed before pairs are built. These answers shaped the framework interface but did **not** block M1-01 (the framework binds pairs abstractly regardless).

1. **P5 feasibility — NEEDS A NEW BUILD (the §6 highest-risk dependency is real).** The FATF engine's `Typology` enum is exactly `{STRUCTURING, RAPID_MOVEMENT, LARGE_TRANSFER}` — all three are *fund-movement* typologies keyed on amounts/timing/velocity/thresholds. There is **no recipient / unauthorized-destination / sanctions-style typology**, and no watchlist/screening anywhere in `core.fatf`. (The "jurisdiction" concept in core is *regulatory-obligation* jurisdiction — EU/INDIA for `core.obligations` — **not** recipient screening; transactions carry a `recipient_account` string but nothing matches it against a flagged-recipient list.) So P5 as *tool-misuse → recipient screening* requires a genuinely new detection mechanism. **Decision still deferred to M1-05 start per §6**, but the recon confirms the fallback is the likely path: if building a recipient-screening typology is more than a small, well-bounded addition, fall back to a clean fourth injection×typology pair (3 clean + 1 boundary + 1 clean). The framework already represents P5's eventual outcome via the **OPEN** result class, and a recipient attack would ride the `TOOL_CALL` channel the framework already models.

2. **P2 distinctness — CONFIRMED genuinely separable (no collapse risk).** `_detect_rapid_movement` is a distinct rule from `_detect_structuring`: different band (rapid uses *no* sub-threshold band; structuring is `[5_000, 10_000)`), different window (`rapid_window = 1h` vs `structuring_window = 24h`), different min-count (`rapid_min_transfers = 5` vs `structuring_min_transfers = 3`), different signal shape (fan-out by `recipient_count` vs sub-threshold total), and a distinct `Typology` enum value + severity. P2's pattern (≥5 fast transfers fanning out within an hour) is structurally different from P1's (≥3 sub-threshold transfers over a day). **Caveat for M1-02:** the *generated* P2 pattern must be authored to fire `RAPID_MOVEMENT` while remaining visibly distinct from P1's structuring cluster — the detectors are independent, but a single dense cluster could in principle trip both; M1-02 must verify P2's stream fires rapid-movement and reads as fast-onward, not sub-threshold-many.

3. **OWASP version pinning — deferred to the paper pass** (citation accuracy, not a build blocker for M1-01). LLM01/LLM06/LLM08 are carried as identifiers on the framework's attack side; confirm against the 2025 list at M1-06.

4. **Reconcile existing constants — DONE.** M1-01 expresses P1 *through* the framework as `P1_PAIR` without redefining `MEMO_INJECTION_SIGNATURE` / `CANONICAL_MEMO_EXPLOIT`: the attack side holds the canonical `MEMO_INJECTION_SIGNATURE` object (single source of truth, bound by identity), and `seam_fraud_stream` / `resolve_signature` / `prove_seam` keep their signatures so every existing caller (the Layer-1 milestone, the demo runner) is unchanged. All existing seam tests pass unchanged — the faithfulness proof.

---

_End of M1-00. This is the paper's methodology backbone and the build sequence's design contract. Next: M1-01 — the seam framework abstraction, with P1 as its first passing instance._
