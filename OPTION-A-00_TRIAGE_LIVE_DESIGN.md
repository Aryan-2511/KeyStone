# Option A · Live Triage Agent — Design & Methodology

**Team BigBird · Keystone · OPT-A-00 (design artifact, no code)**

> **What this is.** The methodology for taking the **Triage Agent** from a transparent policy to a genuine **LLM-reasoned** router — the first "live" agent. It settles what "live" honestly means, how the offline-deterministic front door (the console arc + AppTest gate) stays working regardless, and how we report — truthfully — when the LLM is actually reasoning vs. when it falls back. This is the deck's stated mentor-frontier ("live multi-agent execution"), built now that there's no deadline riding on it.
>
> **Why Triage first.** It's the smaller, safer live conversion: ONE reasoning call over three already-computed signals, not a minutes-long Garak scan. We learn the live-agent pattern (LLM call + record/replay + honest fallback) on the easy agent before the heavy Red-Team/Garak build.
>
> **Why design-first (the honesty questions live here).** "The LLM decides the route" introduces three real risks a judge would probe: (1) non-determinism vs. our reproducibility guarantees, (2) the 3B-on-4GB reliability question we've deferred since MB, (3) the temptation to *claim* LLM reasoning while shipping a fallback. This doc fixes the answers before code.
>
> **Companion:** `MB-00_TRIAGE_AGENT_DESIGN.md` (the policy this upgrades — the §2 interplay bar still applies), `MA-00` (the agency bar), `DECISIONS.md` (ADR on Option-B-before-A). The console arc (offline front door) must survive this unchanged as the default.

---

## §1 · The claim Option-A (Triage) establishes

**Current state (Option B):** the Triage Agent routes remediate/accept/escalate via a transparent policy over (failure_rate, seam_result, severity). Genuinely agentic (route depends on signal interplay), but reasons via explicit rules, honestly labelled "not an LLM."

**Option-A (Triage) claim:**

> **The Triage Agent can route via genuine LLM reasoning: given the finding's signals, an LLM (qwen2.5:3b local / NIM-hosted) reasons about what the finding warrants and returns one of the three routes, with a stated rationale. The LLM's decision is constrained to the real 3-option space and grounded in the real signals — and when the LLM is unavailable or unreliable, the system falls back to the proven Option-B policy, transparently.**

We claim **"the Triage Agent reasons with an LLM when run live"** — NOT "the Triage Agent always reasons live" (the default is offline/policy) and NOT "the LLM is more correct than the policy" (unproven — see §5).

### Honest scope
- **Live = an opt-in mode**, not the default. The offline console arc and AppTest gate keep using the deterministic path (policy or recorded LLM trace). Live is the *upgrade a mentor opts into*, never a requirement to see the system work.
- We do **not** claim the LLM is *better* than the policy — only that it's *genuine LLM reasoning* over the real decision. Whether it matches/beats the policy is an honest open evaluation (§5), not an assumed win.
- We keep the **§2 interplay bar** (MB-00): whatever routes, the route must still depend on the signal *combination*, not collapse to one threshold. The LLM must be shown to honor interplay too (§5 test).

---

## §2 · What "live" genuinely means here (the mechanism, honestly)

The live Triage Agent, concretely:
1. **Reads the real signals** — (failure_rate, seam_result, severity) — the SAME already-computed, read-only inputs the policy uses. It does NOT reach into detection (the memo-blind boundary holds — §4).
2. **Prompts an LLM** (qwen2.5:3b via Ollama, or NIM-hosted llama-3.1-8b — §3) with those signals and the three allowed routes, asking it to choose one and give a one-line rationale.
3. **Constrains the output** to exactly {remediate, accept, escalate} — parse/validate the LLM's answer; an out-of-space or unparseable answer is a failure, handled by fallback (§3), never silently coerced.
4. **Returns the route + the LLM's rationale**, recorded on the RunResult (so replay is faithful).

**This is genuine agency by the strict bar** (reason→decide over a real ≥2-option space, decision depends on observed signals), now with an LLM as the reasoner instead of a policy. The honest mechanism label becomes, in live mode, "LLM-reasoned triage" — and ONLY in live mode. In offline/fallback mode it remains "adaptive triage policy." The label must always match what actually ran.

---

## §3 · Model + the honest fallback (the reliability question, answered structurally)

The 3B-on-4GB reliability question (open since MB) gets answered *empirically* by building this — but the design must be safe **regardless of the answer**:

- **Two model paths, both real:** qwen2.5:3b (local/Ollama, offline-capable, free) and NIM-hosted (llama-3.1-8b, more capable, needs network/creds). Build for both; let evaluation (§5) show which is reliable.
- **The fallback is not optional — it's the safety architecture:** if the LLM is (a) unavailable (no Ollama/NIM), (b) times out, (c) returns an unparseable/out-of-space answer, or (d) is disabled — the system **falls back to the Option-B policy** and **records that it did.** The route is always produced; the *reasoner* degrades gracefully.
- **Honesty rule (load-bearing):** the recorded result must state WHICH reasoner produced the route — `llm` (and which model) or `policy_fallback`. Never report a policy-fallback route as an LLM decision. A mentor asking "did the LLM decide this one?" must get a truthful answer from the record.

**Design consequence:** because the fallback is the proven policy, live mode can NEVER be *worse* than offline mode at producing a valid route — it can only add genuine LLM reasoning when the LLM is working. That's the safe shape: live is strictly additive, never a regression.

---

## §4 · Record/replay + the boundary (preserve everything we've built)

- **The offline front door stays the default and stays deterministic.** The console arc (`keystone demo`), `make demo`, and the AppTest gate use the offline path — policy, or a *recorded* LLM trace replayed deterministically. A live LLM call happens ONLY when explicitly requested (`--live` or equivalent). The "clone → it works offline" guarantee we just built is untouched.
- **Record/replay (the UI-02 / MA-01 / MB-01 mechanism):** a live run records the LLM's decision (route + rationale + which model) onto the RunResult. Recorded mode replays it — identical, offline, reproducible. If this needs a schema field (v7→v8) for the LLM rationale/reasoner-tag, it's the v2-lesson discipline: migrate every fixture, own commit, all replay paths green. (Check: can the existing triage block hold a reasoner tag + rationale, or is a bump needed? — §7 open item.)
- **The memo-blind boundary (SACRED):** the live agent reads ONLY the already-computed signals — never the attack channel, never the detector. The LLM prompt contains the signals, NOT the raw memo/attack. The AST import-scan boundary test must still pass with the live agent present. Putting the attack text into the LLM prompt "for better reasoning" is the exact landmine — forbidden.
- **Determinism preserved:** recorded==fresh holds for the offline/recorded path; hash-chain re-verifies; offline-default intact. Live mode is non-deterministic BY DESIGN (that's what live means) — which is precisely why it's opt-in and record/replay exists.

---

## §5 · The honesty tests + the open evaluation

- **Interplay preserved (the §2 MB bar, now for the LLM):** feed the live agent the same-rate/different-seam scenarios from MB-01. A genuine reasoner should still route differently by context. If the LLM ignores interplay (routes purely on one signal), that's a finding about the LLM's quality — report it honestly; the policy fallback still honors interplay.
- **Constrained-output test:** the live path only ever emits {remediate, accept, escalate}; malformed LLM output triggers fallback, never a coerced/invented route. Test with a stubbed LLM returning garbage → asserts clean fallback.
- **Reasoner-honesty test:** the recorded result's reasoner-tag matches what actually ran (llm vs policy_fallback) — a stubbed-unavailable LLM records `policy_fallback`, a working stub records `llm`. This is the "never claim LLM while shipping fallback" guarantee, as a test.
- **The open evaluation (honest, not assumed):** does the LLM's routing AGREE with the policy's, and when it differs, is it *better* or *worse*? Build a small comparison over the existing findings: LLM route vs policy route, side by side. We do NOT assume the LLM wins. The honest deliverable is "here's where they agree/differ" — which itself is interesting (and tells us if 3B is reliable enough to trust). This is evaluation, not a pass/fail gate.
- Standard gates: offline tests green unchanged; make check/verify green; mypy/Ruff/import-linter clean.

---

## §6 · What Option-A (Triage) produces / does NOT

**Produces:** a Triage Agent that can route via genuine LLM reasoning (live/opt-in), with a proven policy fallback, honest reasoner-labelling, record/replay preserving the offline default, the boundary intact, and an honest LLM-vs-policy evaluation. The first genuinely-live agent — the deck's frontier, real.

**Does NOT:**
- Does NOT make live the default (offline console arc stays the front door).
- Does NOT claim the LLM is better than the policy (open evaluation, not assumed).
- Does NOT take the Red-Team Agent live (that's the next build — real Garak, heavier).
- Does NOT touch the arc's other stages, the schema's meaning, FATF, the seam, or the ledger.
- Does NOT feed the attack channel to the LLM (boundary sacred).
- Does NOT report a fallback as an LLM decision (reasoner-honesty).

---

## §7 · Build sequence & open items

| Step | Produces |
|---|---|
| **OPT-A-00** (this doc) | the claim, what "live" means, the fallback architecture, the honesty tests |
| **OPT-A-01** | live Triage Agent: LLM-reasoned routing + policy fallback + reasoner-tagging + record/replay + boundary intact + the LLM-vs-policy evaluation. First live agent. |
| **(then) OPT-A-02** | live Red-Team Agent (real Garak + optional LLM probe selection) — the heavier build, informed by what OPT-A-01 taught us about live reasoning on this hardware. |

**Open items to confirm in OPT-A-01:**
1. **Model access:** confirm qwen2.5:3b runs via Ollama on the dev machine, and/or the NIM path has working creds. Test the actual reasoning quality early (the deferred 3B question).
2. **Schema:** can the triage block hold a reasoner-tag (`llm:qwen2.5:3b` / `policy_fallback`) + the LLM rationale without a bump, or is v7→v8 needed? Prefer no bump if the block can carry it.
3. **Prompt design:** the signals→route prompt must be constrained and reproducible-in-shape; design it so the LLM's job is bounded selection (which 3B can do) not open reasoning (which it may not).
4. **The evaluation surface:** where the LLM-vs-policy comparison lives (a script/report), so it's honest and inspectable, not buried.

_End of OPT-A-00. The first live agent's design contract — genuine LLM reasoning, safe by fallback, honest by record. Next: OPT-A-01 (build), then the live Red-Team Agent._
