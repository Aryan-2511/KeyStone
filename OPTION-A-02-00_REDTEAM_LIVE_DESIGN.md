# Option A · Live Red-Team Agent (real Garak) — Design & Methodology

**Team BigBird · Keystone · OPT-A-02-00 (design artifact, no code)**

> **What this is.** The methodology for taking the **Red-Team Agent** genuinely live: running **real Garak probe scans** against the target instead of replaying the recorded defense profile — while keeping the adaptive **policy** for probe selection (which works) and explicitly **compute-gating the LLM-reasoned selection** (which OPT-A-01 proved 3B can't do reliably). The offline console arc stays the deterministic default; live Garak is opt-in. This makes the offensive worker's scanning *real*, not characterized — the hardware-independent half of the live-agent frontier.
>
> **Why this split (the OPT-A-01 lesson, applied).** OPT-A-01 empirically showed qwen2.5:3b collapses on even a bounded 3-way choice with clean numeric inputs (agreed 1/6, misread the failure_rate, ignored interplay). Probe selection is a *harder* reasoning task — so LLM-reasoned selection would re-derive that finding at greater cost. We build the genuinely-valuable, LLM-independent half (real Garak) now, and mark LLM-selection as blocked on capable inference (the NVIDIA compute ask, now evidence-backed).
>
> **Companion:** `MA-00_REDTEAM_AGENT_DESIGN.md` (the agent + the §2 honesty bar this preserves), `OPTION-A-00_TRIAGE_LIVE_DESIGN.md` (the live pattern: opt-in, record/replay, fallback, honest tagging — mirror it), `DECISIONS.md` (ADR-0021, the 3B evaluation finding). The console arc (offline front door) survives unchanged.

---

## §1 · The claim OPT-A-02 establishes

**Current state (MA-01):** the Red-Team Agent selects probes via an adaptive policy (scout-then-exploit over 23 prompt-injection probes) but OBSERVES outcomes from the offline `RECORDED_DEFENSE_PROFILE` — a documented characterization anchored to one real capture. The scan is not live.

**OPT-A-02 claim:**

> **The Red-Team Agent can run its probes as REAL Garak scans against the target (live/opt-in): actual probe execution, actual observed outcomes, feeding the same adaptive selection policy. The offensive worker's observations become genuinely live — and when Garak is unavailable, the system falls back to the recorded profile, transparently tagged. Probe SELECTION stays the adaptive policy; LLM-reasoned selection is explicitly deferred to capable inference (OPT-A-01's finding).**

We claim **"the Red-Team Agent runs real Garak scans when live"** — NOT "the agent reasons with an LLM" (selection is the policy, honestly), and NOT "live is the default" (offline recorded path stays the front door).

### Honest scope (what's real, what's characterized — state it plainly)
- **Live = real Garak probe execution** over the prompt-injection families the agent already selects across. Actual scans, actual pass/catch outcomes.
- The **matrix (Movement 1) stays characterized** — P2–P5 remain deterministic characterizations (MA-00's standing caveat). Live Garak makes the *agent's live scan* real; it does not re-derive the whole matrix. Same honest boundary as always.
- **Selection is the policy, not an LLM** — unchanged, honestly labelled. LLM-selection is compute-gated, documented in OPEN_QUESTIONS with OPT-A-01 as the evidence.
- Real Garak scans are **slow (minutes) and environment-dependent** — which is exactly why live is opt-in and record/replay exists (§4).

---

## §2 · What "live" genuinely means here (the mechanism, honestly)

The live Red-Team Agent, concretely:
1. **Selects a probe** via the existing adaptive policy (scout-then-exploit) — unchanged.
2. **Executes it as a REAL Garak scan** against the target (the vulnerable mock agent / the configured target), via the real Garak invocation the codebase already has (`-m slow` path). Actual probe run.
3. **Observes the REAL outcome** (got through / caught) from Garak's actual output, and feeds it to the policy's next selection — so the adaptation is driven by genuinely-observed live results.
4. **Records the live decision trace** (probe sequence + real outcomes) onto the RunResult, tagged as a live scan (vs. recorded profile).

This preserves the **§2 agency bar** (MA-00): the next probe still depends on the observed outcome — now the outcome is *real* instead of profiled. The honest mechanism label in live mode: "adaptive offensive policy over **real Garak scans**." In offline/fallback mode: "adaptive offensive policy over the recorded defense profile." The label always matches what ran.

---

## §3 · Source-of-observations + the honest fallback (mirror OPT-A-01)

Mirror the OPT-A-01 fallback architecture exactly — it's the proven safe shape:
- **Two observation sources, both real in their own sense:** live Garak (real scans, slow, needs Garak + target running) and the recorded defense profile (offline, deterministic, the anchored characterization).
- **The fallback is the safety architecture:** if Garak is unavailable / the target is unreachable / a scan times out or errors → fall back to the recorded profile and RECORD that it did. The scan result is always produced; only the *observation source* degrades.
- **Source tagging (the honesty guarantee):** every red-team decision records its observation source — `garak_live` or `recorded_profile`. Never report a recorded-profile outcome as a live scan. A mentor asking "was this a real scan?" gets a truthful answer from the record. (Same discipline as OPT-A-01's reasoner-tag.)
- **Consequence:** live mode can never be *worse* than offline at producing a valid scan trace — it can only make the observations real when Garak is working. Strictly additive, never a regression.

---

## §4 · Record/replay + the boundary (preserve everything)

- **The offline front door stays the default and deterministic.** `keystone demo`, `make demo`, the AppTest gate all use the recorded profile (or a recorded live trace) — offline, no Garak needed. A real Garak scan happens ONLY on explicit opt-in (`--live` / the live flag, consistent with OPT-A-01). The "clone → it works offline" guarantee is untouched.
- **Record/replay:** a live Garak run records the real probe sequence + real outcomes onto the RunResult; recorded mode replays deterministically. Because scans are minutes-long, the recorded trace is ALSO what makes a live run reviewable afterward without re-scanning.
- **Schema:** check first — can the red_team block hold a source-tag (`garak_live` / `recorded_profile`) without a bump? Prefer no bump (mirror OPT-A-01, where the reasoner-tag fit without one). If a bump is genuinely needed, own commit + migrate every fixture (v2 lesson).
- **The memo-blind boundary (SACRED):** live Garak changes WHERE observations come from, NOT the boundary. The agent stays offense-side; real scan outcomes must NEVER flow into the L1 detector. The 4 lock points hold; the AST import-scan boundary test must still pass with the live scan path present. A real scan feeding detection = the convergence thesis collapses — forbidden.
- **Determinism preserved:** recorded==fresh for the offline/recorded path; hash-chain re-verifies; offline default intact. Live Garak is non-deterministic/slow BY NATURE — precisely why it's opt-in with record/replay.

---

## §5 · The honesty tests + the operational reality

- **Source-honesty test:** stub Garak unavailable → the trace records `recorded_profile`; a (stubbed or real) successful scan → records `garak_live`. Asserts the source-tag matches what ran. (The "never report recorded as live" guarantee, as a test.)
- **Fallback test:** Garak unreachable / target down / scan error → clean fallback to the recorded profile, valid trace produced, tagged `recorded_profile`. Never a fabricated "live" outcome.
- **§2 agency preserved:** the selection policy still adapts to observed outcomes — with live Garak, feed a real (or realistically-stubbed) scan where a family gets through vs. blocked → the sequence still flips. (MA-00's honesty test, now over live observations.)
- **Offline default unchanged:** the console arc / AppTest produce identical results with NO Garak (recorded profile) — the front door works without any live infra.
- **The operational note (honest, in the PR):** report the real cost — how long a live scan actually takes, what infra it needs (Garak version, the target running), and that this is why it's opt-in. Not a failure — the honest operational profile a mentor needs.

---

## §6 · What OPT-A-02 produces / does NOT

**Produces:** a Red-Team Agent that runs REAL Garak scans (live/opt-in), with the recorded profile as a transparently-tagged fallback, the adaptive policy for selection (honestly not-an-LLM), record/replay preserving the offline default, the boundary intact, and an honest operational profile of what live scanning costs. The offensive worker's observations become genuinely real — the hardware-independent half of the live frontier.

**Does NOT:**
- Does NOT add LLM-reasoned probe selection (compute-gated; OPT-A-01 is the evidence; logged in OPEN_QUESTIONS).
- Does NOT make live the default (offline recorded path stays the front door).
- Does NOT re-derive the matrix (Movement 1 stays characterized; live makes the *scan* real, not the matrix).
- Does NOT feed real scan outcomes into detection (boundary sacred).
- Does NOT report a recorded-profile outcome as a live scan (source-honesty).
- Does NOT touch the Triage Agent, FATF, the seam, or the ledger.

---

## §7 · Build sequence & open items

| Step | Produces |
|---|---|
| **OPT-A-02-00** (this doc) | the claim, what live-Garak means, the fallback/source-tag, the boundary, the honesty tests |
| **OPT-A-02-01** | live Red-Team Agent: real Garak scans + recorded-profile fallback + source-tagging + record/replay + boundary intact + the honest operational profile. The offensive worker, genuinely live. |

**After this:** the live-agent frontier is honestly complete for current hardware — Triage can LLM-reason (opt-in, policy-default per OPT-A-01), Red-Team can real-scan (opt-in, recorded-default). LLM-reasoned selection for BOTH agents is the documented, evidence-backed compute-gated frontier — the NVIDIA ask.

**Open items to confirm in OPT-A-02-01:**
1. **Garak + target:** confirm the real Garak invocation (`-m slow` path) still runs, the Garak version, and the target (vulnerable mock agent) is reachable for a real scan. Report a real scan's actual duration.
2. **Probe resources:** Garak re-fetches probe data (deleted in the old disk crunch) — confirm disk headroom and that the fetch works (Step -1).
3. **Source-tag schema:** can red_team hold `source` without a bump? Prefer no bump.
4. **Scan scope:** a full 23-probe live scan may be very slow — decide if the live path runs the policy's actual selected sequence (honest) or a bounded subset for tractability (also honest if labelled). Report what it does.

_End of OPT-A-02-00. The offensive worker goes genuinely live — real scans, honest fallback, boundary intact, LLM-selection compute-gated. Next: OPT-A-02-01 (build)._
