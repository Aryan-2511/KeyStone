# Keystone — Multi-Agent Feasibility (READ-ONLY probe 2)

**Premise (already decided):** we ARE building a multi-agent system (≥2 genuine agents).
**This probe answers:** which components can become *honest* agents (real ≥2-option decision
space; reason → act → adapt), and whether to build them as **NAT agents** or **hand-rolled
reasoning loops**.

**Method:** read-only; every claim cites file·function or an installed-package fact. "Agent"
= reasons + has ≥2 actions not predetermined + adapts on observation. A step with **one**
fixed choice is **not** an agent, and I say so.

**Status:** no code/test/doc changed; this is an untracked workspace file, not committed.

---

## Part 1 — NAT agent machinery (the build-shape question)

### What's actually installed
```
nvidia-nat        1.7.0
nvidia-nat-atif   1.7.0
nvidia-nat-core   1.7.0
```
(`pyproject.toml:14` declares only `"nvidia-nat>=1.7"` — **no extras**, e.g. no
`nvidia-nat[langchain]`.) No `nvidia-nat-langchain` / `-agno` / `-crewai` / `-llama-index`
/ `-semantic-kernel` plugin is present.

### Are the prebuilt agents importable? No.
```python
# probed live:
import nat.agent                      -> ModuleNotFoundError
import nat.agent.react_agent          -> ModuleNotFoundError
import nat.agent.tool_calling_agent   -> ModuleNotFoundError
import nat.agent.reasoning_agent      -> ModuleNotFoundError
import nat.plugins.langchain          -> ModuleNotFoundError
```
- The base install ships only the **config base** `AgentBaseConfig(FunctionBaseConfig)`
  (`.venv/.../nat/data_models/agent.py:23`, *"Base configuration class for all NAT
  agents"*, fields `llm_name: LLMRef`, `verbose`, …) — a **schema**, not a runtime.
- NAT's scaffold template references `_type: react_agent`
  (`nat/cli/.../templates/config.yml.j2:15`), but that `_type` is **not registered** in this
  install (the import above fails) — the concrete ReAct/tool-calling/reasoning agents ship
  in the **framework plugin packages**, which are not installed.
- `nvidia-nat-atif` is **not** an agent runtime: it is an *Agent-Trajectory* eval/observability
  data-model package — `nat/atif/agent.py:30` `class Agent(BaseModel)` is a Pydantic
  *description* of a trajectory (`name`, `version`, `model_name`), alongside
  `metrics.py`, `observation.py`, `step.py`. It describes agent runs; it does not run agents.

### Verdict
**We cannot build genuine NAT prebuilt agents as-is.** Two build-shapes are available:

- **(A) Adopt NAT-native agents** → add a plugin dep (`nvidia-nat-langchain` or similar).
  Cost: pulls LangChain/LangGraph (+ large transitive trees) into a stack that today is
  deliberately lean and offline (`guard.py:6-7` "no model download"; the 4 GB box). It also
  imports a second agent-abstraction on top of the existing clean `keystone.llm.inference`
  seam.
- **(B) Hand-roll reasoning loops in plain Python**, keep NAT as the **orchestrator/sequencer**
  it already is (`agents/orchestrator/functions.py` `register_function` + `load_workflow`),
  and reason through the existing single inference seam (`llm/inference`, with
  `complete_with_tools` already available — `inference/tools.py:62`).

**Recommendation: (B) hand-roll.** The reasoning loop we need (choose-attack → observe →
choose-next) is a dozen lines over the existing `run_scan`/`parse_report`; NAT adds nothing
to that loop, and pulling a framework plugin fights the offline/lean constraints for no gain.
Use NAT to *orchestrate* the agents (it already wraps the loops as functions); put the
*reasoning* in `keystone.assurance`. (If NAT-native agents become a hard requirement later,
(A) is a clean add — `AgentBaseConfig` is there to subclass — but it's not needed for honest
agency.)

---

## Part 2 — Genuine decision spaces (which agents can be HONEST)

### Red-team / offense — **real ≥2-option space EXISTS (large), today unused**
- The code constrains itself to **one** probe: `garak_probe.py:52`
  `CURATED_PROBES = ("latentinjection.LatentInjectionTranslationEnFr",)`.
- But the option space already recognized is **two families**: `garak_probe.py:55`
  `PROMPT_INJECTION_FAMILIES = frozenset({"latentinjection", "promptinject"})`.
- **Garak v0.15.1's actual library (enumerated live, `garak --list_probes`): 230 probes**,
  of which **23 sit in those two prompt-injection families** —
  `latentinjection.*` ×17 (e.g. `LatentInjectionReport`, `LatentInjectionResume`,
  `LatentWhois`, `LatentJailbreak`, `LatentInjectionTranslationEnZh`, …) and
  `promptinject.*` ×6 (`HijackHateHumans`, `HijackKillHumans`, `HijackLongPrompt`, …).
- The integration is **already parameterized** for selection:
  `garak_probe.py:295` `ScanConfig.probes: Sequence[str] = CURATED_PROBES`, passed straight
  to Garak's CLI `--probes` (`:316`). So selecting a *different* / *next* probe is a
  string-list change, not new plumbing.
- **Plus an attack-TYPE taxonomy already in code:** the seam matrix registry
  (`assurance/pairs.py:18` `REGISTERED_PAIRS = (P1..P5)`) characterizes **3 OWASP attack
  classes across 3 channels**: P1/P2/P3 = `LLM01` Prompt-Injection on `MEMO`
  (×structuring / ×rapid-movement / ×large-transfer — `seam.py:132`, `seam_p2.py:109`,
  `seam_p3.py:107`); P4 = `LLM06` Sensitive-Info-Disclosure on `EXFIL` (boundary,
  `seam_p4.py:101-108`); P5 = `LLM08` Excessive-Agency on `TOOL_CALL` (`seam_p5.py:140-142`).
- **Honesty caveat (which is live vs characterized):** only **P1** has a **live** Garak scan
  (`scan_mock_agent`, `garak_probe.py:367`). P2–P5 are **deterministic characterizations** —
  e.g. `seam_p2.py:_p2_recognize` / `_p2_plant` / `_p2_detect` are pattern recognizers +
  planted streams, no live attack. So the **live** offense option space today = Garak's 23
  prompt-injection probes (one model target); the matrix is the *taxonomy* the agent can reason
  over, not 5 live attacks. **Smallest real live attack menu = the 23 prompt-injection probes
  (≥2 by a wide margin).** → **A red-team agent here is honest.**

### Defense / remediation — **one option today; a real menu must be BUILT (and is thin)**
- Today it is genuinely **single-choice**: `loop.py:37` `CONTROL_NAME =
  "nemo-guardrails-input-rail"` (a constant, recorded at `loop.py:164`); the config has exactly
  one rail (`guardrails/config.yml` → `flows: [check data field injection]`); the detector is
  one binary check: `injection_patterns.py:48`
  `return any(pattern.search(text) for pattern in _INJECTION_PATTERNS)`.
- **A ≥2-option menu CAN be built, but cheaply-and-honestly is the question.** NeMo Guardrails
  natively supports **input / output / dialog / retrieval** rails (`guard.py:39`
  `GenerationOptions(rails={...})` already toggles them), so candidate remediations exist:
  {input-rail block (today) · output-rail filter the tool-call · tighten the pattern set ·
  add an allow-list of authorized recipients}. **But** for these to be *honest* agent options
  they must produce **observably different outcomes** the agent can choose between — and today
  all four collapse to "block the one memo-injection." **So defense is a real agent ONLY after
  we build ≥2 remediations with distinguishable effects.** A defender that "chooses" among
  options that all do the same thing is **agency-theater** — do not ship it as agent #2 until
  the menu is real.

### Triage / routing — **no decision today, but a real one maps onto EXISTING observable state**
- Flow is fixed: the loop runs all five stages unconditionally (`loop.py:120-191`); there is
  **no** patch/escalate/accept fork.
- But the observable inputs for a genuine routing decision **already exist**:
  `GarakFinding.failure_rate` (`garak_probe.py:90`), `is_hit` (`:97`), the mapped severity
  (`FAMILY_MAPPINGS`, `:132`), and the matrix outcome enum
  `SeamResult ∈ {CLEAN, BOUNDARY, OPEN}` (`framework.py:67-69`). A triage agent could route a
  finding → {**remediate now** (CLEAN, high failure_rate) · **accept as boundary** (BOUNDARY,
  P4) · **escalate to human** (OPEN / ambiguous)} — a real ≥2-option decision over **state
  that is already computed**. → **A triage/routing agent is honest with little new data.**

### Any other ≥2-option point worth an agent? No.
- The narrative faithfulness (`report_narrative.py:83`) and deontic phrasing
  (`phrasing.py:96`) are **binary validation switches** (model-text vs template), not action
  policies — not agents.
- FATF detect, seam-bind, ledger are deterministic by design (Part 3) — must NOT become agents.

---

## Part 3 — The honest multi-agent recommendation

### The two agents to build (each with a real, cited, non-single-choice decision space)

1. **Red-Team Agent (offense)** — **decision space EXISTS, large.**
   Action set: choose which probe(s) to run next from Garak's **23** prompt-injection probes
   (`garak --list_probes`; selectable via the already-parameterized
   `ScanConfig.probes`/`--probes`, `garak_probe.py:295,316`), reasoning over prior
   `GarakFinding.failure_rate` (`:90`) — escalate to harder probes where the target resisted,
   pivot family where one stalls. Adapt loop: reason → pick probe → run `run_scan` → parse →
   pick next. **Not single-choice** (23 options). **Build-shape: hand-rolled loop** over the
   existing scan/parse functions.

2. **Triage/Routing Agent (the second honest agent)** — **decision space maps onto EXISTING
   state.**
   Action set: route a (finding, mapping, SeamResult) → {remediate · accept-as-boundary ·
   escalate-to-human}, deciding on `failure_rate` (`garak_probe.py:90`), `SeamResult`
   (`framework.py:67`), and the mapped severity (`:132`). **Not single-choice** (3 routes over
   real observable inputs). **Build-shape: hand-rolled policy/LLM classifier.**

*(Deferred third candidate — Defense/Remediation Agent — is honest ONLY after Part-2's ≥2
remediation menu is built. Until then it is single-choice; do not dress the one rail as an
agent.)*

### Topology
- The **adversarial offense↔defense loop** (red-team vs blue-team) is the most *compelling*
  demo and maps onto the existing `EXPOSED→DETECTED→MAPPED→PATCHED→VERIFIED` arc
  (`loop.py:51`). **But** it requires a genuine defender, whose decision space is **thin
  today** (Part 2). Shipping the adversarial loop *now* would make the "defense agent"
  single-choice — theater.
- The topology that matches **where real decisions actually exist today** is
  **offense agent + triage/supervisor agent**: the Red-Team Agent has the richest live
  decision space (23 probes), and the Triage Agent routes its findings over already-computed
  observable state. This is a **supervisor/worker** shape (triage supervises; red-team is the
  offensive worker), honest from day one.
- **Path to the adversarial loop:** once the Part-2 remediation menu (≥2 distinguishable
  rails) is built, promote the defender to a real agent and close offense↔defense. So:
  start supervisor+worker (offense+triage), grow into adversarial (offense+defense) when the
  defender's option space is real.

### What MUST stay deterministic (and why)
- **FATF detection** — `engine.py:14` *"each a deterministic rule with NAMED, configurable
  thresholds"*. Auditability requires identical firing every run; an LLM here destroys
  defensibility. **No agent.**
- **Seam-bind** — `framework.py:190` `bind` is a structural assertion (single-source-of-truth
  identity check + drift error); the independence guarantee is **typed**, not judged. **No
  agent.**
- **Ledger / sign-off** — hash-chained `append` + `verify_chain`; the chain *is* the
  reproducibility guarantee. **No agent.**

---

## Part 4 — The collisions (so the build preserves what works)

### Record / replay (preserve offline-default, recorded==fresh, AppTest gate, hash-chain)
Each agent's **live decisions become first-class recorded data**, replayed deterministically —
the exact mechanism UI-02 already uses for the arc (`demo/run_result.py` save/load; the
`recorded==fresh` test `tests/test_run_view.py:47-54`):
- Red-Team Agent → record the **chosen probe sequence** (+ each `GarakFinding`); replay re-runs
  the *recorded* sequence, not a fresh reasoning pass.
- Triage Agent → record the **route chosen per finding**; replay reads the recorded route.
- The decision trace is **data on `RunResult`/the ledger**; replay is deterministic, so the
  AppTest gate (no Ollama — `test_run_app.py`) and the hash chain stay reproducible.
- **Cost flagged:** a decision trace is a **new field on `RunResult`** → a versioned,
  migrate-all-fixtures schema bump (the project treats these as careful, owned changes —
  `demo/run_result.py:33`). Plan it as its own step.

### Memo-blind boundary (the independence guarantee the convergence paper rests on)
This is **structurally enforced today** and must remain so under agents:
- `framework.py:82-107` — `CrimeSide.detect` is **typed** to accept only a
  `FinancialProjection`, which `project_financial` builds by **blanking the memo**
  (`txn.model_copy(update={"memo": ""})`, `:106`). The detector *structurally cannot* read the
  attack channel.
- `framework.py:198-201` — `bind` hands the detector the **projection only**, never
  `event.stream`.
**Enforce at every one of these places — no agent may bypass them:**
1. **The Red-Team Agent reads/mutates the attack channel (memo/tool_call/exfil) — allowed,
   it's offense** — but its output must reach the crime detector **only** through
   `project_financial` (never a raw `Transaction` stream).
2. `CrimeSide.detect`'s type signature (`framework.py:137`) must stay `FinancialProjection`-only
   — it is the structural lock; do not loosen it to take raw streams for "agent convenience."
3. The FATF engine entry (`core/fatf/engine.detect`) must stay memo-blind; the core must keep
   never-importing `keystone.assurance` (import-linter KEPT — `framework.py:34-36`).
4. Any new agent lives in `keystone.assurance` (the edge), never in `keystone.core` — so an
   agent literally cannot be wired into the detector.
**Landmine:** the single most dangerous change would be giving a triage/defense agent the raw
attack-bearing event "to be smarter" and letting that path touch detection. The type system
forbids it today; keep it forbidden.

### Offline / 4 GB-GPU (can the agents reason on the offline default?)
- The offline default model is small: `garak_probe.py:373` `ollama_model="qwen2.5:3b"`; the
  rail uses **no** model (`guard.py:6-7`).
- A 3B model can do **constrained selection** (pick a probe from a menu; route on
  thresholds) — i.e. classification-shaped decisions — but **not** open-ended planning.
  Quality on 3B is **undetermined** without a live trial; mitigate by keeping each agent's
  action set a **tight menu** (choose-among-N), not free-form tool orchestration.
- **Escape hatch (the same record/replay):** reason **live** (on whatever model the stage box
  has — possibly bigger/online during a real run), **record the decision trace**, and **replay
  it offline** for the demo + the fast tests. So the offline guarantee is preserved regardless
  of the live model: offline = replay a recorded trace; live = reason now.

### Scope — smallest honest path to ≥2 agents, incrementally (Movement-style)
1. **Movement A — Red-Team Agent.** Hand-rolled reason→choose-probe→observe→adapt loop over
   `run_scan`/`parse_report`; decision trace recorded. Gate: a `-m slow` live test (like the
   existing live Garak scan, `garak_probe.py:7`) + a fast test that replays the recorded trace
   (inject the decision like `LoopDeps`/`backend` are injected today — `loop.py:60`,
   `report_narrative.py:71`). Ship, stabilize.
2. **Movement B — Triage/Routing Agent.** Route findings over existing observable state
   (`failure_rate`, `SeamResult`, severity); decision trace recorded; same test pattern. Ship,
   stabilize. **← ≥2 genuine agents reached here.**
3. **Movement C (optional, later) — Defense menu + Defense Agent.** First build ≥2
   distinguishable remediations (Part 2), *then* the agent that chooses among them — closing
   the adversarial offense↔defense loop. Do **not** start here; without the menu it's theater.

NAT stays the orchestrator throughout (wrap each agent as a registered function, as the loops
are today); reasoning is hand-rolled in `keystone.assurance`; no LangChain/LangGraph plugin
unless NAT-native agents become a hard requirement.

---

## Bottom line
- **Build-shape:** hand-rolled reasoning loops + NAT for orchestration. Prebuilt NAT agents are
  **not installed** (`nat.agent` → ModuleNotFoundError; only `AgentBaseConfig` + templates),
  and pulling them in fights the offline/lean stack.
- **The two honest agents:** **Red-Team Agent** (real, large live decision space — 23 Garak
  prompt-injection probes, already-parameterized selection) and **Triage/Routing Agent** (real
  3-way decision over already-computed `failure_rate`/`SeamResult`/severity). Topology:
  **supervisor (triage) + offensive worker (red-team)** now; grow into **adversarial
  offense↔defense** only after a genuine ≥2-remediation menu is built (today defense is
  single-choice — not an agent).
- **Keep deterministic:** FATF detect, seam-bind, ledger — auditability, structural
  independence, reproducibility.
- **The non-negotiables for the build:** (1) record each agent's decisions and **replay** them
  (preserves offline-default, recorded==fresh, the AppTest gate, the hash chain); (2) **never**
  let any agent route the raw attack channel into the memo-blind detector — the type lock at
  `framework.py:137` / `project_financial` must stay intact.

### Appendix — evidence sources
Installed packages (`importlib.metadata`); live imports of `nat.agent.*` (all
ModuleNotFoundError); `nat/data_models/agent.py`, `nat/atif/agent.py`; `garak --list_probes`
(v0.15.1, 230 probes, 23 prompt-injection); `assurance/{garak_probe,loop,guard,framework,
pairs,seam,seam_p2..p5,injection_patterns}.py`, `assurance/guardrails/{config.yml,rails.co,
actions.py}`; `core/fatf/engine.py`; `pyproject.toml`. Undetermined (flagged): 3B-model
reasoning quality; exact non-prompt-injection probe applicability; the schema cost of the
decision-trace field.
