# Movement A · The Red-Team Agent — Design & Methodology

**Team BigBird · Keystone · MA-00 (design artifact, no code)**

> **What this is.** The methodology backbone for the first genuine agent in Keystone: an **offensive red-team agent** whose attack choices *adapt to observed defenses*. It defines the claim, the strict bar that makes this a real agent (not a loop in costume), the record/replay discipline that preserves the demo's determinism guarantees, and the memo-blind boundary that protects the convergence thesis. Doubles as the paper's "agentic" section.
>
> **Why design-first, and why stricter here.** The probe (`multi_agent_feasibility.md`) proved Keystone is currently a deterministic pipeline. Adding an "agent" is exactly where overclaiming creeps in — a `for`-loop over 23 probes is NOT an agent. This doc fixes the bar *before* code so the result is genuinely agentic and survives a judge opening the hood. The honesty test is concrete and testable (below).
>
> **Companion docs:** `multi_agent_feasibility.md` (the feasibility evidence this builds on), `M1-00` (the matrix the probes attack), `KEYSTONE_REGULATORY_REFERENCE.md`. **Path A reframing lands before this** (honest language first).

---

## §1 · The claim Movement A establishes

**Current state:** the L2 red-team is a *fixed scan* — one constant probe (`CURATED_PROBES`), detect, re-scan with the same probes. No choice, no adaptation. Deterministic.

**Movement A claim:**

> **Keystone's offensive testing is performed by a genuine agent: it reasons over the observed outcomes of the attacks it has tried, and adapts its next attack choice based on what is getting through versus what the defenses caught — selecting from a real library of 23 prompt-injection probes (Garak). The agent's attack sequence is a function of observed defenses, not a predetermined list.**

This is the first component in Keystone that meets the strict agent bar: **reason → act → observe → adapt**, with a genuine ≥2-option decision space (23 probes) where the next action is *not* predetermined.

### Why this is honest (and the boundary of the claim)
- **Live decision space = the 23 probes** in the two prompt-injection families the code recognizes (Garak v0.15.1 ships 230; 23 in-family). This is real and adaptive.
- **Honest caveat (stated, not hidden):** only P1 is a *live* scan; P2–P5 of the seam matrix are deterministic characterizations. So the agent's *live adaptation* operates over the 23-probe injection space — we claim adaptive offensive testing **within the live attack surface**, not "an agent that re-derives the whole matrix." The matrix remains the characterized result (Movement 1); the agent makes the *live* offense adaptive.
- **We do NOT claim** open-ended planning or autonomous goal generation. The agent does *bounded adaptive selection* — which is (a) genuinely agentic (next action depends on observation) and (b) honestly within what qwen2.5:3b can do reliably offline.

---

## §2 · The agency bar (what makes this an agent, not a for-loop) — THE load-bearing section

A loop that runs all 23 probes in a fixed order is **deterministic iteration**, not agency. The agent bar, stated strictly and made **testable**:

> **An agent's next choice must demonstrably depend on what it observed. Change what the early probes "find," and the agent's later choices must change. If the sequence is the same regardless of observations, it is a loop, not an agent.**

This is the **honesty test** for Movement A, and it is a literal test (§5):
- Run the agent against a defense where family X gets through and family Y is blocked → it should escalate within X, deprioritize Y.
- Run it against the inverse (Y gets through, X blocked) → its choices should *flip*.
- If the two runs produce the *same* probe sequence, the "agent" is fake — the build fails.

The agent must have, explicitly:
1. **State it observes:** the outcome of each probe tried (succeeded / caught by guardrail), accumulated.
2. **A reasoning step** that maps observed-outcomes → next-probe-choice (LLM-reasoned or a transparent policy — see §3).
3. **A genuine ≥2-option action space:** ≥2 probe families, ≥2 probes per family, so "choose" is meaningful.
4. **Adaptation:** the choice at step N depends on outcomes of steps 1..N-1.

If any of these is absent, it is not an agent — do not ship it as one. (The probe's "agency-theater" warning applies in full.)

---

## §3 · The reasoning step — two honest options, pick the one that holds on 4GB

The agent needs a reason→choose step. Two honest implementations; the build picks based on what qwen2.5:3b can do *reliably* (test it):

- **Option A — LLM-reasoned selection (preferred if the model holds):** the agent prompts qwen2.5:3b with the outcomes-so-far and the available probe families, and the model *reasons* about what to try next ("instruction-override is being caught; data-field injection got through; try more data-field variants"). Genuinely agentic, demo-compelling. **Risk:** 3B may be unreliable at this; MUST be tested, and MUST degrade gracefully.
- **Option B — transparent adaptive policy (the honest fallback):** a bandit-style / rule-based selector where the next probe maximizes exploitation of the family that's succeeding (e.g. "escalate within the highest-success family; abandon families fully blocked"). This is STILL an agent by §2's bar — the next choice depends on observed outcomes — it just reasons via an explicit policy rather than an LLM. **Honest framing:** if we ship Option B, we call it "an adaptive offensive policy," not "an LLM agent." Don't overclaim the mechanism.

**Design rule:** whichever ships, the §2 honesty test must pass (choices flip when observations flip). The mechanism (LLM vs policy) is described *honestly* in the docs and the paper. **Prefer A; ship B if A isn't reliable offline; never claim A while shipping B.**

---

## §4 · Record/replay — preserving the demo's determinism (non-negotiable)

A live-reasoning agent acts differently each run. This collides with the offline-default, the `recorded==fresh` replay test, the no-Ollama AppTest gate, and the hash-chain — *all at once* (the probe spelled this out). The resolution (the UI-02 mechanism, already proven):

> **Live mode:** the agent genuinely reasons and adapts (real agency). **Its decision trace is recorded** — the sequence of (observed-outcomes → chosen-probe) steps — onto the RunResult/ledger.
> **Recorded mode:** replay the decision trace deterministically. Identical reveal, reproducible, offline, AppTest-safe.

- The recorded run stores the agent's *actual decisions*, so replay is a faithful playback of a real agentic run — honest on both sides (not faked, not re-computed).
- **Schema bump cost:** the decision trace needs a home on RunResult (likely schema v6). Migrate every fixture, keep all replay paths green (the v2 lesson), own commit. The trace is derived from the run, not hand-authored.
- The AppTest gate runs against the *recorded* trace (offline) — so the agent never needs live inference for tests to pass.

---

## §5 · The honesty test + the other gates

- **THE honesty test (the one that matters):** flip the observed outcomes → the agent's probe sequence flips. Same observations → same sequence; different observations → different sequence. This is what proves it's an agent, not a loop. (If it can't pass, it's not an agent — STOP.)
- **Memo-blind boundary (sacred):** the agent lives on the OFFENSE side. It must NEVER feed the attack channel / raw memo to the L1 detector. The 4 structural lock points named in the probe (`framework.py:137`, `project_financial:106`, etc.) must not loosen. An agent "reading the attack to be smarter" that touches detection = the convergence thesis collapses. Test: independence invariants still hold with the agent in the loop.
- **Determinism preserved:** recorded==fresh still green; offline-default intact; hash-chain re-verifies; AppTest green against the recorded trace.
- **The matrix unchanged:** Movement 1's characterized result is untouched; the agent makes *live offense* adaptive, it does not re-derive the matrix.

---

## §6 · What Movement A produces / what it does NOT

**Produces:** one genuine agent (Red-Team Agent) — observe→reason→adapt over 23 probes — with record/replay, the honesty test, the memo-blind boundary intact, and honest docs/paper language about the mechanism.

**Does NOT:**
- Does NOT make the defense agentic (that's Movement C, gated on a real ≥2-remediation menu — building a defender now is agency-theater).
- Does NOT add the Triage Agent (that's Movement B — the second agent, which makes it formally multi-agent).
- Does NOT pull NAT-native agents / LangChain into the lean stack (hand-rolled loop + NAT orchestration — per the probe).
- Does NOT touch the deterministic core (FATF detect, seam-bind, ledger) — those stay deterministic by design.
- Does NOT claim open-ended autonomy — bounded adaptive selection, honestly scoped.

---

## §7 · Build sequence & dependencies

| Step | Produces |
|---|---|
| **Path A reframing** (before MA) | honest language now ("becoming multi-agent"); fix the `keystone.agents` overclaim |
| **MA-00** (this doc) | the claim, the agency bar, the honesty test, record/replay, the boundary |
| **MA-01** | the Red-Team Agent: observe→reason→adapt over 23 probes; the honesty test passing; record/replay (schema bump); memo-blind intact. **First genuine agent.** |
| **(then) MB** | the Triage Agent → **two agents = multi-agent system** (the requirement, met honestly) |
| **(later) MC** | defense menu + defense agent → adversarial loop (optional, gated on real remediations) |

**The order matters:** MA gives one honest agent; MB makes it multi-agent. We are honest at every checkpoint — never claiming multi-agent until MB lands, never claiming "agent" until MA's honesty test passes.

---

## §8 · Open items to confirm before MA-01
1. **qwen2.5:3b reasoning reliability:** can it do Option-A LLM-reasoned probe selection reliably offline? Test early; fall back to Option B (adaptive policy) if not — and frame honestly.
2. **The 23-probe surface:** confirm the Garak probe families + that `ScanConfig.probes` selection works as the feasibility probe found (parameterized Sequence).
3. **Decision-trace schema:** confirm the record/replay trace fits on RunResult with a clean v? bump migrating every fixture.
4. **Independence invariants:** confirm the 4 memo-blind lock points and that a test asserts they hold with the agent present.

_End of MA-00. The first genuine agent's design contract — built so it survives a judge opening the hood. Next: MA-01 (the Red-Team Agent), then MB (Triage) for the multi-agent pair._
