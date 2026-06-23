# Movement 2 · Regulatory Convergence as a First-Class Feature — Design & Methodology

**Team BigBird · Keystone · M2-00 (design artifact, no code)**

> **What this document is.** The methodology backbone for Movement 2: turning "AI-security findings are *analogous* to compliance failures" (a sentence in the knowledge base) into "a seam event *is* the audit evidence that satisfies-or-violates a named, real regulatory obligation" (a thing the system computes, across EU + India, grounded in real before/after data). It defines the claim, the rigor bar that separates this from checklist RegTech, the satisfy-vs-violate model, the named obligations we map, and the honest boundaries.
>
> **Why before any code.** Movement 2's failure mode is not a broken build — it's building a *compliance dashboard* that demos fine but doesn't make the novel claim. "Make convergence a feature" can mean three different things; this doc pins which one, so M2-01+ build to the claim and not to something fuzzier. Doubles as the paper's convergence-contribution section.
>
> **Companion docs:** `M1-00_SEAM_MATRIX_DESIGN.md` (the matrix this evidences), `KEYSTONE_KNOWLEDGE_BASE.md` §5 (the obligations + enforcement-modality concept), `KEYSTONE_RESEARCH_AND_NOVELTY.md` §2C/§6 (the convergence-from-regulation finding this operationalizes).

---

## §1 · The claim Movement 2 establishes

**Current state (Movement 1):** the seam proves an AI-security failure and a financial-crime failure are the same *event*. Layer 3 (governance) holds regulatory obligations, but somewhat in parallel — the seam event and the obligations don't yet *flow into each other*.

**Movement 2 claim:**

> **A seam event is not merely *analogous* to a compliance failure — it *is* the audit evidence that satisfies-or-violates a named, current regulatory obligation. The same artifact the red-team found and the AML engine caught is the evidence a compliance auditor needs for a specific control — and its satisfy-or-violate state is grounded in real before/after data, reconciled across EU hard law and India's advisory regime.**

This closes the loop the project has only gestured at: the three layers stop being parallel and become a **pipeline** — attack found (L2) → caught as crime (L1) → *bound as one event* (the seam) → **evidenced against named obligations with a satisfy/violate state (L3)**. The output is a compliance posture an auditor can act on, evidenced by an exact event.

### Why this is the biggest remaining novelty gain
The research (`RESEARCH_AND_NOVELTY` §2C, §6) found that **ISO 42001 and NIST AI RMF are beginning to *require* prompt-injection controls** — AI-security is *becoming* a named compliance obligation. The thesis is arriving from the regulatory direction. Movement 2 operationalizes that: it makes the seam event the *evidence* for those emerging obligations, demonstrated across two regulatory philosophies. No prior work (per our search) treats an AI-security red-team finding as cross-jurisdiction compliance audit evidence.

---

## §2 · The rigor bar (the anti-"checklist RegTech" defense)

The novelty lives entirely in the **rigor of the evidence relationship**, not the *count* of obligations. Mapping many obligations shallowly is mundane RegTech and a reviewer will dismiss it. So the bar — analogous to M1's independence guarantee — is:

> **Every seam-event → obligation mapping must state a specific, defensible reason WHY this event is evidence for this obligation, grounded in the obligation's actual text/requirement — not a drawn line on a slide.**

Concretely, a rigorous mapping must answer all four:
1. **Which obligation** (named, cited, real — with its enforcement modality).
2. **What the obligation actually requires** (the specific control/text — e.g. ISO 42001's risk treatment for "input manipulation and unauthorized instruction modification").
3. **Why this seam event is evidence for/against it** (the defensible link — the event *is* an instance of the input-manipulation the control addresses).
4. **Satisfy or violate, and on what data** (the before/after state — see §3).

A mapping that can't answer all four is **not admissible** — same discipline as a seam pair that can't prove independence. **Narrow-and-deep: 3-4 obligations, each rigorously evidenced, beats a broad shallow sweep.**

---

## §3 · The satisfy-vs-violate model (grounded in before/after)

The subtle question a reviewer *will* press: does a seam event **satisfy** an obligation or **violate** it? The honest answer is **both — depending on the moment** — and the system already has the data to ground this (the L2 assurance before/after: ~10/12 attacks succeed pre-patch → 0/12 post-patch).

> **The same obligation is VIOLATED pre-patch and SATISFIED post-patch — and the seam event is the evidence for both states.**

- **Pre-patch (the finding / violation):** the attack succeeded — the AI was manipulated and moved laundered money. The event is evidence the obligation was **violated** (EU Art. 15 robustness failed; the AML monitoring obligation was at risk). This is the *risk* state.
- **Post-patch (the satisfied control):** the assurance loop **detected and patched** the vulnerability, and the monitor **caught** the transaction. That detection-and-response is *exactly* what ISO 42001 / NIST AI RMF require you to *demonstrate*. The event is evidence the obligation is now **satisfied**. This is the *controlled* state.

**Why this is the most compelling thing Movement 2 can show:** it makes "AI-security finding = compliance evidence" **concrete and temporal**, not a static checkbox. The before/after the project already produces (10/12 → 0/12) becomes a *compliance state transition*: "here is the same obligation, violated then satisfied, evidenced by the same seam event." That is the convergence, made auditable.

> **Design consequence:** the evidence model (M2-01) must carry BOTH states and the data behind the transition, not a single satisfy/violate flag. The state is a function of (obligation, before/after assurance data), derived — not asserted.

---

## §4 · The named obligations (narrow-and-deep; all already cited)

Four obligations, spanning both jurisdictions and both modalities, each already in the knowledge base with citations. Each must clear the §2 four-part bar.

| Obligation | Jurisdiction | Modality | What it requires | Why the seam event evidences it |
|---|---|---|---|---|
| **ISO 42001** (input-manipulation control) | International std | Advisory/certifiable | Risk assessment + treatment for "input manipulation and unauthorized instruction modification" | The memo-injection IS input manipulation / unauthorized instruction modification — the exact risk the control names |
| **NIST AI RMF** (semantic-threat modeling) | US (voluntary framework) | Advisory | Threat modeling for semantic attack vectors | Prompt injection is the semantic attack vector; the seam event is a realized instance |
| **EU AI Act Art. 15** (`OBL-EUAI-015`) | EU | **Hard law** (€15M/3% tier) | Accuracy, robustness & cybersecurity for high-risk AI | The agent was successfully manipulated → robustness/cybersecurity finding; post-patch → control demonstrated |
| **RBI FREE-AI Sutra 1** "Trust is the Foundation" (`OBL-RBI-001`) | India | **Advisory** (convertible) | Trustworthy AI as foundational principle | The attack undermines trust; the assurance loop restores it — the sutra evidenced as a control state |

> **The modality spread is deliberate** (and ties to Movement-1-style two-axis sampling): ISO/NIST/RBI are advisory; EU Art. 15 is hard law. So Movement 2 shows the SAME seam event evidenced against obligations of *different enforcement weight* — the cross-jurisdiction half of the claim. India spans advisory (RBI) while EU is binding (Art. 15) — the real per-obligation modality (KB §5.1), not country-inferred.

### Boundary obligation (the honest negative, M1-style)
Just as P4 was the matrix's characterized boundary, Movement 2 should be honest about an obligation the seam event does **NOT** cleanly evidence — e.g. a *data-protection* obligation (DPDP) that the *exfil boundary case (P4)* would evidence but the fund-movement seam does not. This keeps the mapping honest: not every obligation is evidenced by every event; the evidence relationship is specific. **(Candidate: DPDP data-protection ↔ only the P4 exfil class, not the P1-P3/P5 fund-movement events.)**

---

## §5 · What each Movement-2 task produces (the build sequence M2-00 unblocks)

| Task | Produces |
|---|---|
| **M2-00** (this doc) | The claim, the rigor bar, the satisfy/violate model, the named obligations. Paper's convergence-method section. |
| **M2-01** | The **evidence model** — a typed structure binding a seam event to the obligation(s) it evidences, carrying BOTH satisfy/violate states + the *reason* + the before/after data behind the transition. Derived, not asserted. The analog of M1-01's framework. Likely touches Layer 3. |
| **M2-02..** | Each named obligation's rigorous evidence relationship to the matrix (the §2 four-part mapping), with before/after state. Includes the boundary obligation (§4). |
| **M2-0n** | The **convergence result + UI**: the loop made visible — "this seam event → these named obligations, violated→satisfied, EU hard-law + India advisory." Likely schema bump + a screen. The paper's convergence figure. |

Dependency chain: **M2-00 (design) → M2-01 (evidence model) → M2-02.. (mappings) → M2-0n (result/UI).** Same "build the dependency before the thing that needs it" discipline.

---

## §6 · Risks, fallbacks, honest scoping

- **The "checklist RegTech" collapse (highest risk):** if mappings become drawn lines without the §2 four-part reason, the novelty evaporates. Guard: every mapping states WHY, grounded in obligation text. A mapping that can't is dropped, not fudged.
- **Overclaiming the legal interpretation:** we are not lawyers. The mappings are *defensible technical-compliance reasoning* ("this event is an instance of the risk this control names"), NOT legal advice or a certified compliance opinion. State this boundary explicitly (mirrors the KB's "representative, not certified" honesty on report schemas).
- **Satisfy/violate oversimplification:** real compliance is rarely binary. The before/after model is a *defensible simplification* (violated pre-patch, satisfied post-patch); note that real audits weigh more factors. Honest scoping, not a claim of complete compliance determination.
- **The boundary obligation must be real, not token:** the DPDP-only-evidences-P4 boundary (§4) must be as principled as P4 itself — data-protection obligations are evidenced by data-loss events, not fund-movement events. Don't force it; if it doesn't hold cleanly, find the honest one.
- **Scope to what's shown:** the paper claim is "we demonstrate seam events as cross-jurisdiction compliance evidence for these 4 named obligations, with a before/after state model" — NOT "we determine full regulatory compliance." Never widen beyond the evidenced obligations.
- **Modality must stay real per-obligation** (KB §5.1): never infer satisfy/violate weight by country; read the obligation's actual modality.

---

## §7 · Open items to confirm before M2-01

1. **L3 integration point:** how does the existing Layer-3 obligation/control data structure represent obligations, and where does the evidence model attach? (M2-01 likely extends L3 — confirm the existing shape so the evidence model subsumes it cleanly, like M1-01 subsumed the seam.)
2. **Before/after data availability:** confirm the L2 assurance before/after (10/12 → 0/12, the REFERENCED_ASSURANCE constant) is reachable from where the evidence model will compute the satisfy/violate transition — it should be (it's in the RunResult already from KS-0503's v3 bump).
3. **Boundary obligation feasibility:** confirm a data-protection obligation (DPDP) exists or can be added to L3 to serve as the §4 boundary (evidenced only by P4 exfil). If not cleanly, pick the honest alternative boundary.
4. **Obligation citations:** confirm the ISO 42001 / NIST AI RMF control references are pinned accurately (KB §7.4 / RESEARCH §2C have them) for the paper.

### §7a · Step-0 L3 recon findings (resolved during M2-01) — locks M2-02+

> Read-only recon over `keystone.core.obligations` + `keystone.core.controls`. These shaped the evidence model (which references L3 abstractly) and lock the obligation set before M2-02. They did **not** block M2-01.

1. **L3 obligation shape — CONFIRMED; evidence model subsumes it cleanly.** `keystone.core.obligations.Obligation` (core, ADR-0012): `id` (`OBL-<PREFIX>-<NNN>` — e.g. `OBL-EUAI-015`, `OBL-RBI-001`, `OBL-DPDPA-008`), `instrument`, `citation` (provision + title), `summary`, `enforcement_modality` (`HARD_LAW` / `SELF_CERTIFICATION`, **real per-obligation**, not country-inferred), `jurisdiction` (`EU`/`INDIA`), and `control_ids` → `keystone.core.controls.Control` (`CTL-<DOMAIN>-<NN>`, with a `spine` onto `ISO_42001` / `NIST_AI_RMF` / `FATF`). The evidence model **references** these by id (`ObligationRef.from_obligation`) — it does NOT create a parallel registry. The reason/requirement attach to the obligation + its control text; L3 itself is unchanged (all 28 obligations + controls stay green).
2. **Before/after reachable — CONFIRMED.** `keystone.assurance.REFERENCED_ASSURANCE` (`prompt_cap=12, before_fails=10, after_fails=0, exploit_before=True, exploit_after=False, remediated=True`) is directly importable on the edge; the evidence model builds its `BeforeAfter` FROM it and derives the state, so it can't drift. (It is also surfaced in the RunResult v4 `ai_security.assurance` block for the eventual UI.)
3. **DPDP boundary obligation — FEASIBLE, already present.** L3 has real DPDP data-protection obligations — `OBL-DPDPA-005/006/008/009/010/011` (DPDP Act, INDIA, HARD_LAW) + `OBL-DPDPR-004/006/007` (DPDP Rules 2025). `OBL-DPDPA-008` (general obligations of the Data Fiduciary → `CTL-SEC-01` security safeguards) is a clean §4 boundary candidate: evidenced by the P4 exfil/data-loss class, NOT by fund-movement events. The M2-01 boundary test uses a DPDP obligation to prove the `NOT_EVIDENCED` structure. **No new obligation needed for the boundary.**
4. **Reference mapping chosen — EU AI Act Art. 15 (`OBL-EUAI-015`).** The cleanest first instance: hard law, EU, and it crosswalks onto `CTL-ROBUST-01` (ISO 42001 Clause 8 + NIST AI RMF MEASURE — robustness/resilience testing), so a single mapping anchors both the "EU Art. 15" and the "ISO 42001 robustness" framings of §4. The memo-injection IS the robustness/cybersecurity failure it names; the assurance loop's detect-and-patch is the resilience testing it requires. ISO/NIST control references are pinned via the control spine; confirm exact clause numbering against KB §7.4 at the paper pass.

---

_End of M2-00. The convergence-contribution methodology + the build sequence's design contract. Next: M2-01 — the evidence model (seam event → obligation, satisfy/violate, derived from before/after), with the existing Layer 3 subsumed cleanly._
