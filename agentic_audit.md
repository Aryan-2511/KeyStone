# Keystone — Agentic Architecture Audit (READ-ONLY probe)

**Question:** Is Keystone genuinely a multi-agent system, a deterministic pipeline, or a
hybrid — and where does each component sit? And what would Path B (building genuine agency)
take?

**Method:** read-only. Every classification below quotes the file + function + a short
excerpt. Where the code did not settle a question I say "undetermined", not a guess.

**Status:** no code/test/doc changed; this report is an untracked file, not committed.

---

## Definitions applied (strictly)

- **AGENT** — genuine agency: (a) decides from reasoning/LLM-output or a policy, (b) the
  next action is *not* predetermined — it depends on what it observes, (c) can
  adapt/loop/choose among options. Tool-use **plus a decision over the result**.
- **DETERMINISTIC STAGE** — fixed logic: input X always produces Y; no reasoning, no
  branch-on-observation beyond ordinary control flow; output is a pure function of input.
  (Neutral/good for some components.)
- **GUARDED LLM CALL** — calls an LLM in a constrained, single-shot way (generate +
  check); the LLM fills a slot, it does not choose actions or adapt.
- **ORCHESTRATOR** — coordinates the others. Sub-note: does it route **on observed
  results** (agentic) or run a **fixed sequence** (pipeline)?

---

## Part 1 — The orchestration (the core question)

### Where NAT is actually used
Three integration points, all using NAT's **function** machinery — not its agent
machinery:

- `src/keystone/agents/orchestrator/config.py:10-40` — every config subclasses
  `FunctionBaseConfig` (not `AgentBaseConfig`):
  ```python
  from nat.data_models.function import FunctionBaseConfig
  class OrchestratorConfig(FunctionBaseConfig, name="keystone_orchestrator"):
      layers: list[str]
  ```
- `src/keystone/agents/orchestrator/functions.py:14-16,32,50,67,95` — registers four
  functions with `@register_function(config_type=...)` (`FunctionInfo.from_fn`). The module
  docstring itself says: *"No business logic and no LLM — each stub only writes one ledger
  entry"* (`functions.py:4-5`).
- `src/keystone/agents/run.py:14,23,32,62` — `load_workflow(...)` loads a packaged YAML and
  invokes it once.

### Is NAT orchestrating distinct agents, or sequencing functions?
**Sequencing functions.** The chassis orchestrator runs a **fixed loop over a config
list**, in order, with no decision:
```python
# functions.py:56-62  build_orchestrator._run
async def _run(message: str) -> str:
    statuses: list[str] = []
    for name in config.layers:               # fixed order from YAML
        stub = await builder.get_function(name)
        result = await stub.ainvoke(message, to_type=str)
        statuses.append(str(result))
    return " | ".join(statuses)
```
The YAML confirms the "agents" are three no-op stubs (`workflow.yml`):
```yaml
workflow:
  _type: keystone_orchestrator
  layers: [layer1_stub, layer2_stub, layer3_stub]
```
The two milestone workflows (`assurance_workflow.yml`, `layer1_workflow.yml`) are a **single
function each** wrapping a synchronous Python loop via `asyncio.to_thread`
(`functions.py:85`, `functions.py:112`) — NAT runs one function; the arc lives in plain
Python.

### Does control flow branch on observed results, or is it a fixed pipeline?
**Fixed pipeline.** The arcs are hard-coded tuples and run in that exact order regardless of
what is observed:
- L2 assurance: `loop.py:51-57` `ARC = (EXPOSED, DETECTED, MAPPED, PATCHED, VERIFIED)`;
  `run_assurance_loop` (`loop.py:120-191`) executes stages 1→5 unconditionally.
- L1 milestone: `layer1_milestone.py:68-73` `ARC = (INGESTED, DETECTED, SEAM_BOUND,
  REPORTED, SIGNED)`; same straight-line execution.

### The execution graph + decision points
```
run.py:run_layer1()  ──NAT load_workflow──▶ build_layer1_milestone._run
   └─ asyncio.to_thread(run_layer1_milestone)         # layer1_milestone.py
        1 INGESTED   seam_fraud_stream()               # synthetic stream
        2 DETECTED   FATF engine.detect()              # deterministic rules
        3 SEAM_BOUND resolve_signature(memo)           # structural map
        4 REPORTED   draft_report → generate_narrative # 1 guarded LLM call
        5 SIGNED     ledger.append(signed)             # deterministic
```
**Is there ANY point where the system chooses the next step based on reasoning?**
**No.** Every "branch" found is ordinary data-shaping control flow (None-guards, sums,
comprehensions in `demo/convergence.py`, `demo/matrix.py`), never a selection of the next
*action* from an observed *result*. The closest thing to a result-dependent value is the
loop's `remediated` flag (`loop.py:172`), but it is **recorded**, not acted on — the next
stage runs regardless.

---

## Part 2 — Component-by-component classification

| # | Component | File · function | Class | Why (cited) |
|---|---|---|---|---|
| 1 | NAT chassis orchestrator | `functions.py:56` `build_orchestrator` | **ORCHESTRATOR — fixed pipeline** | `for name in config.layers: stub.ainvoke(...)` — fixed order, no routing on results |
| 2 | L2 assurance loop | `loop.py:120` `run_assurance_loop` | **DETERMINISTIC sequence** | runs `ARC` 1→5 unconditionally; `remediated` recorded not acted on |
| 3 | L1 milestone arc | `layer1_milestone.py:68` `ARC` | **DETERMINISTIC sequence** | fixed-tuple arc; straight-line |
| 4 | Red-team (Garak) | `garak_probe.py:52,302,367` | **DETERMINISTIC (fixed scan)** | `CURATED_PROBES` is a fixed list; `run_scan` shells a fixed argv; parse/map pure |
| 5 | Assurance patch (Guardrails) | `loop.py:164`; `guard.py:52` | **DETERMINISTIC (fixed rail)** | `_record(PATCHED, control=CONTROL_NAME)` — constant; `is_blocked` is a pattern rail, **no main LLM** |
| 6 | FATF detection (L1) | `core/fatf/engine.py:14-19,49` | **DETERMINISTIC — a FEATURE** | named-threshold rules (`ctr_threshold`, `structuring_window`); identical firing every run |
| 7 | Seam-bind | `assurance/seam.py:73` `resolve_signature` | **DETERMINISTIC structural op** | maps memo→canonical signature; *"Composition only — no new detection capability"* |
| 8 | Reporting narrative | `llm/report_narrative.py:70` `generate_narrative` | **GUARDED LLM CALL** | one `complete()` then `narrative_is_faithful`; drift ⇒ `template_narrative`. No loop/retry |
| 9 | Obligation phrasing | `llm/phrasing.py:84` | **GUARDED LLM CALL** | one `complete()` + `detect_modal_drift` ⇒ fallback. No loop |
| 10 | Mock payments agent | `assurance/agent.py:127` `run_agent` | **GUARDED LLM CALL (single-turn tool-calling)** | one `complete_with_tools`; mechanically executes returned calls; the **target**, not an orchestrator |
| 11 | Guarded-agent endpoint | `assurance/garak_endpoint.py:46` `guarded_brain` | **GUARDED LLM CALL** | `if is_blocked: refuse; else complete(...)` — single shot |
| 12 | Sign-off / ledger | `core/ledger` (`ledger.append`, `verify_chain`) | **DETERMINISTIC — a FEATURE** | hash-chained append + verify; reproducible by design |

### The five arc steps + the loops, in prose

- **Red-team loop (Garak / L2):** a **fixed scan**, not an adaptive red-team. The probe set
  is a constant: `garak_probe.py:52` `CURATED_PROBES =
  ("latentinjection.LatentInjectionTranslationEnFr",)`, and `run_scan` (`:302`) builds a
  fixed argv and shells Garak once. The loop does detect → patch → **re-**scan
  (`loop.py:139,167`), but **both scans use the same fixed probes** — there is no
  find→reason→choose-a-different-attack feedback. Parsing, mapping (`FAMILY_MAPPINGS`,
  `:132`), and the "found our vulnerability?" check (`:189`) are all deterministic. **Not an
  agent.**
- **Assurance / patch (NeMo Guardrails):** the remediation is **predetermined**, not chosen.
  `loop.py:37` `CONTROL_NAME = "nemo-guardrails-input-rail"` is a module constant; the PATCH
  stage just records it (`loop.py:164`). The rail itself (`guard.py:39-63`) runs
  **input-only, pattern-based** rails with **no main LLM** and reads `activated_rails` to
  decide block/allow. The patch does not reason over the finding. **Not an agent.**
- **Detection (FATF / L1):** **deterministic — correctly so.** `engine.py:14` *"each a
  deterministic rule with NAMED, configurable thresholds"* (`ctr_threshold=10_000`,
  `structuring_window=24h`, etc., `:49-62`). A regulator needs identical firing every time;
  this is a **feature**, not a deficiency.
- **Seam-bind:** a **fixed structural operation**, not a decision. `seam.py:73-82`
  `resolve_signature` deterministically maps a positive memo detection to
  `CANONICAL_MEMO_EXPLOIT.signature`; the docstring states *"Composition only — no new
  detection capability, no redefined signature."*
- **Reporting (LLM narrative + faithfulness):** a **GUARDED LLM CALL**, single pass. It
  generates **once** and checks **once**:
  ```python
  # report_narrative.py:80-85
  drafted = complete(_facts_prompt(facts), system=NARRATIVE_SYSTEM, backend=backend).strip()
  if drafted and narrative_is_faithful(drafted, facts):
      return GuardedNarrative(text=drafted, fell_back=False)
  return GuardedNarrative(text=template_narrative(facts), fell_back=True)
  ```
  On failure it **falls back deterministically** — it does **not** loop, retry, or refine.
- **Sign-off / ledger:** **deterministic** — `ledger.append` writes a hash-chained entry;
  `verify_chain` recomputes. Reproducible by construction. **A feature.**
- **Every other LLM call:** the inventory is complete — `agent.py:149`
  (`complete_with_tools`), `garak_endpoint.py:46`, `phrasing.py:84`, `report_narrative.py:80`
  (all `complete`). The backends (`llm/inference/ollama.py:39,70`) are **single
  `httpx.post`** calls, no loop. **There is no agentic LLM loop anywhere.**

---

## Part 3 — Evidence of agency that may already exist

Searched specifically for: adaptive loops, LLM-output-drives-control-flow, policy selection,
check-driven retry.

- **Adaptive loops (find → decide → act-differently):** **none found.** The two "loops"
  (`run_assurance_loop`, `run_layer1_milestone`) are fixed-order tuples; the Ollama/NIM
  clients issue one HTTP call (`ollama.py:39`).
- **LLM output determining control flow:** **none.** LLM output is always consumed as
  *content to validate*, never as a *next-action selector*. In the mock agent
  (`agent.py:153-155`) the model's tool calls are filtered against a fixed signature
  (`if call.name != MEMO_INJECTION_SIGNATURE.exploit_tool: continue`) and mechanically
  recorded — the agent does not decide what to do *next* based on them.
- **Policy/decision logic selecting among options on observed state:** **none.** The only
  selections are static table lookups (`FAMILY_MAPPINGS[...]`, `garak_probe.py:180`) and the
  faithfulness/deontic **binary guards**, which choose *model-text vs template* — a
  validation switch, not an action policy.
- **Retry/refine driven by a check failing:** **none.** Both guards fall back on first
  failure (`report_narrative.py:85`, `phrasing.py:97`); neither re-prompts.

**Plain statement:** the current system is **orchestration-of-deterministic-stages plus
single-shot guarded LLM calls** — pipeline-shaped. There is **no existing agency to
surface** in the strict sense. (Path A would be *framing*, not *uncovering* — see Part 4.)

---

## Part 4 — The honest verdict

**Keystone today is (ii) a deterministic pipeline with guarded LLM calls — not a multi-agent
system, and not a hybrid in any agentic sense.** Proportion, by the Part-2 table: **7
deterministic** components (incl. the two orchestration sequences and the NAT "orchestrator"
that runs a fixed fan-out) and **5 guarded/single-shot LLM calls**. **Zero** components meet
the AGENT bar (decide → act-differently-on-observation → adapt/loop). NAT is used as a
**function runner / sequencer**, not an agent framework — the package is literally named
`keystone.agents` but contains NAT *functions* whose own docstrings say "no LLM, just
orchestration" (`functions.py:75`, `:104`). This is the **honest** answer the brief asked
for, and for this product it is largely the *right* shape: an evidence/assurance system
wants determinism and reproducibility, not a model improvising the audit.

**Best candidates to become genuine agents** (ranked):
1. **Red-team (Garak) — strongest.** Red-teaming is *intrinsically* a reason→attack→observe→
   adapt loop; the current fixed single-probe scan is the least-natural fit for determinism.
2. **Assurance/patch — second.** Choosing a remediation from a finding is a genuine decision
   space (which rail / which mitigation), today collapsed to one constant.

**Must stay deterministic** (do **not** dress these as agents):
- **FATF detection** — auditability requires identical firing; an LLM here would destroy
  defensibility (`engine.py:14`).
- **Seam-bind** — it is a structural integrity guarantee, not a judgment (`seam.py:78`).
- **Sign-off / ledger** — the hash chain *is* the reproducibility guarantee.
- **The faithfulness/deontic guards** — these are deliberately deterministic *checks on* the
  LLM; making them "agentic" would defeat their purpose.

---

## Part 5 — Feasibility of making it genuinely (hybrid-)agentic

### The red-team agent (most promising)
- **Current shape:** a fixed scan. `garak_probe.py:52` `CURATED_PROBES` (one probe);
  `run_scan` (`:302`) passes `--probes` a fixed comma-join and parses the JSONL report
  (`parse_report`, `:147`). `ScanConfig.probes` (`:295`) is *parameterizable* but always
  supplied a constant by callers (`scan_mock_agent`, `:367`).
- **Does Garak expose programmatic attack selection?** Partially: the integration drives
  Garak **per-invocation via CLI `--probes`** (`:316`), so attack selection *is* already a
  programmatic input — but it is invoked **once** with a static list, not in a loop.
- **Smallest real change that makes it adaptive:** wrap `run_scan` in a **decision loop**
  outside Garak: (1) run probe family F, (2) parse findings, (3) a selector — LLM *or* a
  policy table — chooses the **next** probe based on what failed/passed, (4) repeat until a
  budget/criterion. The genuinely-agentic delta is step 3 choosing F<sub>n+1</sub> from the
  observed F<sub>n</sub> results. This is additive (a new loop over the existing
  `run_scan`/`parse_report`), needs no change to FATF/seam/ledger, and is **the one place a
  reasoning step is defensible** (offensive testing benefits from creativity).

### The assurance agent (second candidate)
- **Current shape:** one constant rail. `loop.py:37` `CONTROL_NAME`; the PATCH stage records
  it (`:164`); `guard.py` always builds the same rail (`build_rails`, `:46`, `lru_cache`).
- **What would change:** introduce a **remediation chooser** that reads the mapped finding
  (`MappedFinding`, `garak_probe.py:138`) and selects among ≥2 real remediations (e.g.
  input-rail vs output-rail vs prompt-hardening) — *then verifies*. To be honest agency it
  must have **a real choice with ≥2 outcomes** and decide from the finding; a chooser with
  one option is still deterministic (agency-theater — see Part 6).

### NAT's actual agent capabilities (available, unused)
- **Version:** `nvidia-nat 1.7.0` (installed).
- **Agent machinery exists:** `.venv/.../nat/data_models/agent.py` defines
  `class AgentBaseConfig(FunctionBaseConfig)` — *"Base configuration class for all NAT
  agents"* — with `llm_name: LLMRef`, `verbose`, etc. NAT's templates reference
  `react_agent` / `tool_calling_agent` / `reasoning_agent`
  (`nat/cli/.../templates/config.yml.j2`).
- **What Keystone uses:** only `FunctionBaseConfig` + `register_function`
  (`config.py:10`, `functions.py:16`). It subclasses **none** of the agent configs.
- **So:** there **is** agent machinery in the framework we are not using. Caveat
  (undetermined without an install check): the concrete prebuilt agent *implementations*
  (ReAct etc.) ship in separate plugin packages (`nvidia-nat-langchain`/`-agno`); only
  `AgentBaseConfig` + templates are present in the base install here. A true-agent path would
  likely need a plugin dependency **or** a hand-rolled loop (the Part-5 red-team option,
  which avoids the dependency).

### The offline / determinism tension (the central Path-B collision)
This is where genuine agency **collides** with what the demo + tests rely on:
- **(a) Offline-default:** the project runs offline by design — the guarded narrative falls
  back to a template, the rail uses **no model** (`guard.py:6-7`), and even "live" mode in
  the UI uses the deterministic template (per the recorded-fallback decision). A **reasoning
  agent needs an LLM deciding actions** — that reintroduces a hard model dependency exactly
  where the project removed it.
- **(b) Deterministic replay:** `demo/run_result.py` saves a run and the UI replays it; the
  whole UI test suite asserts **recorded == fresh build**
  (`tests/test_run_view.py:47-54`). An agent that reasons live will **not** reproduce the
  same decisions run-to-run, breaking `recorded_run.json` reproducibility and that test.
- **(c) AppTest gate:** `tests/test_run_app.py`, `test_shell_app.py` run the real arc with
  **no Ollama** and assert specific artifacts (e.g. `"STRUCTURING"`). A non-deterministic
  agent in the arc would make these flaky.
- **(d) Hash-chained ledger:** the chain hashes payloads; if an agent's choices land in
  payloads, two runs produce **different chains** — the ledger's reproducibility (a selling
  point) weakens unless the decisions are recorded and replayed verbatim.

**The resolution that keeps the guarantees (record/replay the agent's decisions):** make the
agent's **decisions first-class recorded data** — run the agent live *once*, persist its
chosen actions into the run (and ledger), and **replay those recorded decisions
deterministically**. This is feasible and aligns with the existing `record → replay`
spine (`demo/run_result.py`, the recorded-run fixture): the live path reasons, the demo/test
path replays a captured decision trace. It does **not** make the *replay* agentic — it makes
the *live* path agentic and the *demo* path a faithful recording (the same honesty rule UI-02
already applies to the arc).

### The seam's integrity under agency (landmines)
- The seam binding + the L1/L2 **independence** guarantee are structural
  (`seam.py:73`, the matrix's stated independence property in `demo/matrix.py:30`). The
  load-bearing invariant: **L1 (FATF) detects on amounts/timing alone, "memo-blind"** — it
  must **not** read the attack channel (the memo). An adaptive agent is fine on the **L2
  offensive** side (Garak red-team) because that side is *supposed* to manipulate the memo.
  **The landmine:** if an "assurance agent" or any agent were given the memo/attack content
  as input to the **L1/detection** side, it would couple the two layers and **destroy the
  independence claim** that the whole convergence story rests on. Keep any agent strictly on
  the L2 red-team/remediation side; never let it feed the L1 detector.

---

## Part 6 — Risks & open questions for a hybrid conversion

- **Reproducibility:** keep a deterministic recorded-run by **recording the agent's
  decisions and replaying them** (above). Candidate confirmed feasible — it mirrors the
  existing run-save/replay (`demo/run_result.py`) and UI-02's live-vs-recorded honesty rule.
  Open question: schema cost — a decision trace is a new field on `RunResult` (a versioned,
  migrate-all-fixtures change; the project treats schema bumps as careful, owned changes).
- **Offline guarantee / 4 GB-GPU:** genuine reasoning likely needs more than the
  offline default (the rail uses no model; Garak's mock target uses `qwen2.5:3b`,
  `garak_probe.py:373`). A 3B model can *attempt* attack-selection reasoning but quality is
  uncertain (**undetermined** without a live trial). Risk: the "agent" reasons poorly on the
  small model and the determinism you give up buys little. Mitigation: the agent's *decision*
  can be a small policy/LLM step with a tight action set, not open-ended planning.
- **Test stability:** AppTests must run without Ollama. Either (i) the agent path is
  exercised only by a `-m slow` live test (like the real Garak scan today,
  `garak_probe.py:7`) while the fast gate replays a recorded decision trace, or (ii) the
  agent is dependency-injected with a canned decision in tests (the project already
  injects `LoopDeps`/`backend` everywhere — `loop.py:60`, `report_narrative.py:71`). Both
  are idiomatic here.
- **Honesty (avoid agency-theater):** a step with **one** possible choice is deterministic
  no matter how it's dressed. Only convert a step that has a **real** action space with ≥2
  observable-dependent outcomes. By that test: **red-team attack-selection qualifies**
  (many probes, results differ); a **one-rail "patch chooser" does not** until ≥2 real
  remediations exist.
- **Scope (incremental, one agent — like the Movements):** the **smallest honest** Path-B
  is **one** genuinely-adaptive **red-team agent** wrapping `run_scan`/`parse_report` in a
  reason→choose-next-probe→observe loop, with its decision trace recorded for replay. It
  touches only `keystone.assurance` (which the core never imports — `agent.py:14`), needs no
  FATF/seam/ledger change, and can ship behind the existing slow-test boundary. A **full
  multi-agent rebuild** (NAT ReAct agents coordinating L1/L2/L3) is a likely **trap**: it
  fights the offline + reproducibility guarantees on every axis for little demo gain.
- **Demo impact:** the live-execution view (UI-02) reveals 5 fixed arc steps from
  `RunResult.arc` (`ui/run_view.py:arc_steps`). An adaptive red-team agent would add a
  **variable-length** sub-sequence (N attack rounds) — the reveal would need to render a
  *recorded* decision trace (it already renders a recorded run; the same mechanism extends).
  The recorded-run demo stays stage-safe **iff** the agent's trace is recorded, not improvised
  on stage.

---

## Path A vs Path B — recommendation (honest tradeoff)

- **Path A (surface existing agency):** there is **no agentic loop to surface** (Part 3). The
  most honest "Path A" is **re-framing** — stop calling deterministic NAT functions "agents,"
  and present the system truthfully as *NAT-orchestrated deterministic assurance with guarded
  LLM edges*. That is defensible and judge-proof, but it does **not** make the project
  multi-agent; it makes the *claims* accurate. Low effort, high integrity, **no new
  capability**.
- **Path B (build one genuine agent):** convert **the red-team** into a real
  reason→choose-attack→observe→adapt loop, **decision-trace recorded for deterministic
  replay**. This is the *one* place agency is both **natural** (offensive testing wants
  creativity) and **safe** (it lives on the L2 attack side, never touches the memo-blind L1
  detector or the ledger's determinism). Scoped to `keystone.assurance`, gated behind the
  existing slow-test boundary, with the fast gate + demo replaying the recorded trace.

**Recommendation:** **A then a scoped B — in that order.** First make the language honest
(Path A re-framing) so nothing oversells. Then, if a genuine agent is wanted for the story,
build **exactly one** — the **adaptive red-team agent** — using record/replay to preserve the
offline-default, the AppTest gate, the recorded-run demo, and the hash chain. Treat anything
beyond that one agent (an "assurance agent" with a single rail, or a NAT multi-agent mesh) as
**out of scope until it has a real action space**, to avoid agency-theater. The central,
non-negotiable constraint for any Path B: **the agent reasons on the LIVE path only; the
demo and tests replay its recorded decisions** — otherwise reproducibility, offline-default,
and the ledger's integrity all break at once.

---

### Appendix — files read for this audit
`agents/orchestrator/{config,functions,__init__}.py`, `agents/orchestrator/*.yml`,
`agents/run.py`; `assurance/{loop,loop_live(ref),garak_probe,guard,agent,seam,
garak_endpoint}.py`; `assurance/layer1_milestone.py`; `core/fatf/engine.py`;
`llm/{report_narrative,phrasing}.py`, `llm/inference/{base,tools,ollama}.py`;
`demo/{run_result,convergence,matrix}.py`; `ui/run_view.py`; the installed
`nat/data_models/agent.py`. NAT version `1.7.0`.
Undetermined items flagged inline: prebuilt-agent plugin availability; 3B-model reasoning
quality; the exact schema cost of a recorded decision trace.

Path A â honest reframing: done, verified, pushed

Branch path-a-honest-reframing (commit e6622fd, based on clean main @ f9b2b39 which now includes the merged UI-02) is pushed. Open the PR here (base main):
https://github.com/Aryan-2511/KeyStone/pull/new/path-a-honest-reframing

I did not self-merge. Suggested title: Path A: honest reframing â language/naming match reality (no logic change).

Step-0 note (flagged & resolved)

UI-02 wasn't in main when I started (the Step-0 STOP condition â and Path A references UI-02's run-view + edits the same docs files). I surfaced it; you merged it (PR #33), I re-pulled and confirmed run_view.py is on main, then proceeded.

Package-name decision: Option (b) â keep keystone.agents

Confirmed by blast radius (7 files + Makefile + pyproject + the import-linter contract) and by MA-00_REDTEAM_AGENT_DESIGN.md Â§7, which explicitly plans MA-01 to put the Red-Team agent in this package. A rename to keystone.orchestration would be churn that MA-01 reverses. So the name becomes a forward-looking promise (its docstring now says so), not a present-tense false claim.

Every overclaim repaired (the full list)

1. README.md â "Unified multi-agent demo" â "An orchestrated â¦ deterministic by design â¦ becoming a multi-agent system (Red-Team + Triage next, Movements A/B); nothing today is claimed as a reasoning agent."
2. ARCHITECTURE.md â "Multi-agent â¦ system: agents ingestâ¦" â "An orchestrated system: a NAT workflow sequences deterministic stages â¦ becoming a multi-agent systemâ¦"
3. CLAUDE.md â "a multi-agent â¦ system" â "an orchestrated â¦ workflow â¦ becoming a multi-agent system (Red-Team + Triage next)."
4. src/keystone/agents/__init__.py â "Orchestration / agents â¦ Empty until Phase 1" â honest forward-framing: holds deterministic orchestration today (no reasoning, no agent chooses the next step), and is where the genuine MA/MB agents will sit.
5. ROADMAP.md â added a "Becoming a multi-agent system (Movements A/B)" section; "agent" earned only when MA-01's honesty test passes.
6. TASKS.md â added the same forward-framing (Path A done; MA-01 next; A+B = multi-agent).
7. MEMORY.md â the honest self-description is now durable; "agent" reserved for MA-01 (Red-Team) + MB (Triage).

What I deliberately did not touch

- The UI has no "agent" labels (run_view/shell use "ingest/detect/seam-bind/report/sign" as workflow stages) â already honest, left alone (item 4 satisfied).
- feature_list.json had no present-tense overclaim â unchanged (and adding planned MA/MB entries is MA-00's job, not reframing).
- Product/category names that are correct â "NeMo Agent Toolkit", "OWASP Agentic ASI", the "vulnerable mock agent" (the target-under-test) â left as-is.
- The deterministic components' behaviour â FATF detect, seam-bind, ledger â untouched; only described honestly (determinism framed as the feature it is).

Confirmation: no logic/behaviour changed; tests green unchanged

Pure language/naming/comment change. make check / make verify green: 420 passed, 2 skipped â identical to the baseline I captured before editing. mypy strict / Ruff / import-linter clean, no new ignores. No test references the changed strings (verified), so nothing needed updating.

Honest one-liner now in README/MEMORY

â "An orchestrated compliance & assurance workflow on the NVIDIA agentic stack â deterministic by design where auditability demands it, becoming a multi-agent system (genuine Red-Team + Triage agents next, Movements A/B)."

Two things to flag (not blockers)

1. The reframing docs now reference three untracked files â multi_agent_feasibility.md, agentic_audit.md, and MA-00_REDTEAM_AGENT_DESIGN.md (MA-00 pre-existed untracked; the two probe reports were created under the probes' explicit "do not commit" rule). I did not commit them (that's your call, and the probe tasks said not to) â but the references will dangle for a fresh clone until they're committed. Want me to commit them (e.g. into docs/) so the pointers resolve?
2. Disk was 100% full (0 bytes free) mid-task â the write failed once. The drive was already full (my whole session created ~34M against a 454G disk); I reclaimed ~2.7G by clearing regenerable caches I created this session (Garak's downloaded probe resources from the feasibility probe â garak re-fetches on next live run â plus the session scratchpad/screenshots). It's still 100% used / only ~2.7G free, so it'll likely recur â worth a cleanup on your end.

Next: MA-01 â the Red-Team Agent (the first genuine agent), per MA-00.
