# Movement B · The Triage Agent — Design & Methodology

**Team BigBird · Keystone · MB-00 (design artifact, no code)**

> **What this is.** The methodology backbone for Keystone's **second** genuine agent: a **supervisory Triage Agent** that routes a security finding three ways — **remediate / accept / escalate** — by reasoning over the *interplay* of multiple observed signals, not a single threshold. With MA-01 (the Red-Team Agent) + this, Keystone is honestly a **multi-agent system**: two agents, genuine decisions, a supervisor-worker topology. This doc fixes the agency bar before code so the second agent is as real as the first — because "multi-agent" is only honest if *both* agents pass the strict bar.
>
> **Why the bar is strict here (the specific trap).** A 3-way router that collapses to `if failure_rate > X` is a **deterministic threshold**, not an agent. The probe (`multi_agent_feasibility.md`) flagged exactly this risk. The honest Triage Agent's route must depend on the *combination* of signals such that the same value of one signal yields *different* routes depending on the others. The honesty test (below) is concrete and testable, mirroring MA-01's.
>
> **Companion docs:** `MA-00_REDTEAM_AGENT_DESIGN.md` (the first agent; mirror its structure + honesty discipline), `multi_agent_feasibility.md` (the feasibility evidence: the triage decision space exists over already-observable state), `M1-00`/`M2-00` (the seam/convergence the findings come from).

---

## §1 · The claim Movement B establishes

**Current state:** after a red-team finding, control flow is fixed — the system records the finding and proceeds. There is no *decision* about what a finding warrants. The probe confirmed: no triage/routing decision exists today; flow is predetermined.

**Movement B claim:**

> **Keystone's response to a security finding is decided by a genuine supervisory agent: it reasons over the interplay of the finding's observed signals — its failure rate, its seam classification (CLEAN / BOUNDARY / OPEN), and its mapped severity — and routes it to one of three actions (remediate / accept / escalate). The route is a function of how the signals combine, not a single threshold; the same failure rate can route differently depending on the seam context.**

With MA-01, this is the **second** genuine agent — and the one that makes the system formally **multi-agent**:

> **Topology: supervisor–worker.** The Triage Agent (supervisor) reasons about findings produced by the Red-Team Agent (offensive worker). Two agents, genuine decisions each, interacting. This is "multi-agent" in the plain, defensible sense — verifiable by reading the code.

### Honest scope (what we claim, and don't)
- We claim **two genuine agents in a supervisor-worker topology**, each passing the strict agency bar (§2). That is a multi-agent system.
- We do **not** yet claim the *adversarial* offense↔defense loop (that needs a real ≥2-remediation menu — Movement C, gated). "Remediate" here is a *routing decision* (this finding warrants remediation), not the Defense Agent *choosing among* remediations. Stated honestly: the Triage Agent decides *whether/what-priority*, not *which fix* — the fix-selection agent is later.
- We do **not** claim open-ended autonomy — bounded routing over observed state (4GB-safe, honest).

---

## §2 · The agency bar (genuine triage vs a dressed-up threshold) — THE load-bearing section

A router reducible to one `if` on one signal is **not** an agent. The bar, strict and testable:

> **The route must depend on the INTERPLAY of ≥2 signals: the same value of one signal must produce DIFFERENT routes depending on the others. If the route is a pure function of a single signal (a threshold), it is not an agent — it is a rule.**

This is MB's **honesty test**, and it is literal (§5):
- Hold failure_rate FIXED at some value; vary the seam result (CLEAN vs BOUNDARY vs OPEN) and/or severity → the **route must change**. (E.g. a moderate failure rate on a CLEAN result → *accept*; the *same* failure rate on an OPEN/high-severity result → *escalate*. The seam context changes what the finding means.)
- If holding all-but-one signal fixed and varying the others NEVER changes the route, the "agent" is a single-signal threshold — the build FAILS.

The agent must have, explicitly:
1. **Observed state:** the finding's (failure_rate, seam_result, severity) — already computed elsewhere; the agent *reads* them, never recomputes or reaches into detection.
2. **A reasoning step** mapping the *combination* → route (transparent policy; see §3).
3. **A genuine ≥2-option action space:** 3 routes (remediate / accept / escalate), each reachable.
4. **Interplay-dependence:** the route depends on how signals combine, not one threshold.

If the route collapses to a single-signal rule, it is not an agent — do not ship it as one.

---

## §3 · The reasoning step — transparent triage policy (Option B again, honestly)

Mirror MA-01: ship a **transparent policy** (not an LLM) first, framed honestly. The triage policy reasons over the *combination*:
- **escalate** — when the finding is dangerous-in-context: e.g. OPEN seam result (unresolved) with non-trivial failure rate, or high mapped severity regardless of rate (an unresolved/severe finding a human must see).
- **remediate** — when the finding is real and resolvable: e.g. a CLEAN/known seam result with a failure rate above the action floor (the system can and should patch it).
- **accept** — when the finding is contained/低-impact: e.g. a BOUNDARY result (characterized non-binding) or a failure rate below the action floor (nothing actionable).
- The exact cells are the design's content; the REQUIREMENT is that the route depends on the *interplay* (the §2 test passes — same rate, different seam → different route).

**Honest framing:** this is "an adaptive triage policy," NOT "an LLM agent." It is an agent by §2 (route depends on observed combination, ≥2 options, not predetermined) but reasons via an explicit policy. Option A (LLM-reasoned triage) is a later upgrade; never claim A while shipping B. (Same rule as MA-01.)

> **Design caution (avoid agency-theater):** make sure the 3 routes are GENUINELY reachable and that the interplay is real — if in practice every finding routes the same way, or one route is never taken, the decision space is illusory. The §5 tests must show all three routes reachable AND the interplay flipping the route.

---

## §4 · Record/replay + the boundary (inherit MA-01's discipline)

- **Record/replay (§MA-00-4):** the Triage Agent's decision (the route + the signals it saw) is recorded on the RunResult; recorded mode replays it deterministically. Likely a schema bump (v6→v7) for the triage decision trace — migrate EVERY fixture, keep ALL replay paths green (the v2 lesson), own commit. The triage block is DERIVED by running the agent (mirrors red_team/matrix/convergence), not hand-authored. *(Disk-sensitive — check free space first, per MA-01's Step -1.)*
- **The memo-blind boundary (SACRED, §MA-00-5):** the Triage Agent reads only the *already-computed* signals (failure_rate, seam_result, severity). It must NEVER reach into the L1 detector or read the attack channel. Like MA-01, enforce structurally (the agent imports nothing on the detection path; an AST import-scan test asserts it) + the 4 independence locks hold with BOTH agents present.
- **Determinism preserved:** recorded==fresh at the new schema; offline-default intact; AppTest gate runs against the recorded trace; hash-chain re-verifies.

---

## §5 · The honesty tests + gates

- **THE honesty test (the one that proves it's an agent):** hold one signal fixed, vary the others → the route changes. Same combination → same route; different combination → (where it should) different route. Specifically: same failure_rate, different seam_result → different route. If the route never changes when non-target signals vary, it's a threshold — STOP. (Mirror MA-01's flip test.)
- **All-routes-reachable test:** construct findings that each route to remediate, accept, AND escalate — proving the 3-option space is genuine, not 2-of-3-dead.
- **Interplay test:** prove ≥1 case where the SAME failure_rate yields DIFFERENT routes because the seam context differs — the literal "not a single threshold" proof.
- **Boundary:** independence invariants hold with BOTH agents present; the triage agent imports nothing on the detection path (AST scan).
- **Determinism:** recorded==fresh at the new schema; all replay paths green; offline intact.
- make check / make verify green; mypy strict / Ruff / import-linter clean, no new ignores.

---

## §6 · What Movement B produces / does NOT

**Produces:** the **second** genuine agent (Triage Agent — supervisory routing over signal interplay), making Keystone honestly a **multi-agent system** (supervisor + offensive worker). Record/replay, the honesty tests, the boundary intact, honest "policy not LLM" framing.

**Does NOT:**
- Does NOT make the *defense* agentic / choose among remediations (Movement C — gated on a real ≥2-remediation menu; "remediate" here is a ROUTE, not a fix-selection). Stated honestly.
- Does NOT claim the adversarial offense↔defense loop yet.
- Does NOT pull NAT-native agents / LangChain in (hand-rolled policy + NAT orchestration).
- Does NOT touch the deterministic core (FATF detect, seam-bind, ledger) or re-derive the matrix.
- Does NOT claim "agent" where the §2 test doesn't pass; does NOT claim LLM while shipping policy.

---

## §7 · Build sequence & the multi-agent claim

| Step | Produces |
|---|---|
| **MB-00** (this doc) | the claim, the agency bar (interplay not threshold), the honesty tests, the topology |
| **MB-01** | the Triage Agent: route over signal interplay; the §2 test passing; all-routes-reachable; record/replay (schema bump); boundary intact with BOTH agents. **The second genuine agent.** |

**On landing MB-01:** Keystone is honestly **multi-agent** — two agents (Red-Team worker + Triage supervisor), genuine decisions, verifiable by reading the code. *Only then* do the docs/deck/demo claim "multi-agent system" in the present tense. (Until then: "becoming multi-agent," per Path A.)

**Later (gated):** Movement C — a real ≥2-remediation menu + a Defense Agent that CHOOSES among fixes → the adversarial offense↔defense loop. Only when the remediation menu is genuinely ≥2 distinguishable options (else agency-theater).

---

## §8 · Open items to confirm before MB-01
1. **The signals are read-only & already-computed:** confirm failure_rate (GarakFinding), seam_result (SeamResult ∈ CLEAN/BOUNDARY/OPEN), and a mapped severity are all reachable to the triage agent WITHOUT touching detection. (The probe said yes — confirm the access path.)
2. **All three routes are genuinely reachable** with realistic findings (no dead route → no agency-theater).
3. **The interplay is real:** confirm ≥1 (failure_rate, seam) combination where the same rate routes differently by seam context — the basis of the whole "not a threshold" claim. If it can't be made real, the triage agent collapses to a threshold — STOP and rethink the signal set.
4. **Schema bump fits:** the triage decision trace on RunResult, clean v→v+1 migration of every fixture. (Disk check first.)

_End of MB-00. The second genuine agent's design contract — the one that makes "multi-agent" true. Next: MB-01 (the Triage Agent), after which Keystone is honestly a multi-agent system._
