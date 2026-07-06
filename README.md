# Keystone

An **orchestrated compliance & assurance** demo built on the NVIDIA agentic
stack — [NeMo Agent Toolkit](https://github.com/NVIDIA/NeMo-Agent-Toolkit)
(`nvidia-nat`) for orchestration, [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
for policy, and [Garak](https://github.com/NVIDIA/garak) for red-teaming.
**Deterministic by design** where auditability demands it (FATF detection, the seam
binding, the hash-chained ledger) — that determinism is a feature, not a gap — and
now a **complete multi-agent system**: three genuine agents interacting across the seam —
an offensive **Red-Team Agent**, a supervisory **Triage Agent**, and a **Defense Agent**
that chooses which remediation a finding warrants — plus the **closed adversarial loop**
(the Red-Team re-scans the patched target and adapts). Each reasons through an explicit,
observation-driven policy (not an LLM; "LLM-reasoned" is a named later upgrade, Option A).
They are agents by a strict bar: the next action demonstrably depends on what they observed.

## Start here (for reviewers)

**What Keystone is.** A demo of *orchestrated compliance & assurance* for
financial-sector AI: it maps regulatory obligations to a unified control spine,
detects a risk once and renders it into every regulator's report format, red-teams
the guarded surface, and writes tamper-evident evidence to a hash-chained ledger —
deterministic where auditability demands it, with three genuine agents at the edge.

**The three agents (and the loop).** A **Red-Team Agent** (offensive worker) adapts its
next prompt-injection probe to what the last one revealed; a **Triage Agent** (supervisor)
routes each finding — remediate / accept / escalate — on the *interplay* of its signals; a
**Defense Agent** (defender) chooses which remediation the finding warrants from a genuine
≥2-option menu — (a) block the AI-side injection at the guardrail, or (c) tighten the
money-side detection — on the finding's two-sided strength. Then the loop closes: the
Red-Team **re-scans the patched target** and adapts (the exploit that landed 11/12 unpatched
comes back 0/12 once the rail is on; the Red-Team finds the surface closed and abandons it).
All three are observation-driven policies, framed honestly as such — no LLM in any decision.

**The seam thesis.** Detection and reporting are held **independent** by a
memo-blind boundary (mechanically enforced: an AST import-scan test proves the
agents cannot reach the detector). That independence is what makes the convergence
result — a seam event turning named obligations from *violated* to *satisfied* —
trustworthy rather than circular.

**Honest status.** Proven in finance; the design **generalizes structurally**, not
"built for all sectors". The agents are observation-driven policies by default; an
opt-in **live mode** now exists — the Triage Agent can LLM-reason the route (local
qwen2.5:3b) and the Red-Team Agent runs **real Garak scans** — both *inside the trust
boundary*, both with a proven fallback, both honestly tagged for what actually ran.
Two live-agent experiments showed today's small local model can't yet be trusted for the
agents' *decisions* (see [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md) §B) — so the policies
stay the default; capable **on-prem** inference is the evidence-backed compute frontier for
making the agents' decisions LLM-reasoned. Movement C (the Defense Agent + the closed
offense↔defense loop) is **done**; the remaining deferred item is Movement 3 (the system
red-teaming its *own* reasoning), distinct from the offense↔defense loop already built.

**Run it (from a clean clone).** After [Setup](#setup) below:

```sh
uv run keystone demo   # runs the real arc end to end within the trust boundary — no data leaves; no Ollama/Garak/network needed
```

This runs one genuine Layer-1 assurance arc and narrates the actual result it
produced: the FATF finding, the Red-Team Agent's landed exploit, the seam bind,
the Triage Agent's route, the Defense Agent's chosen remediation, and — the finale —
the **adversarial loop** (the Red-Team re-scans the patched target and adapts), all
sealed to the hash-chained ledger. It is deterministic and runs with **zero network** —
the strongest proof of the **data-residency / no-exfiltration** guarantee the product is
built for (sensitive data never leaves the institution's trust boundary; all inference is
local / on-prem). `make demo` is the same command; `make ui` opens the visual Streamlit
version. An opt-in `--live` mode takes the agents live *inside the boundary* (real Garak
scans incl. the real guarded re-scan, local-LLM triage).

**Where to look:** [`ARCHITECTURE.md`](ARCHITECTURE.md) (layers & boundaries) ·
[`DECISIONS.md`](DECISIONS.md) (the load-bearing *why*) ·
[`ARTIFACT_INDEX.md`](ARTIFACT_INDEX.md) (deck, demo video, design docs, probes) ·
[`FINAL_STATE_AUDIT.md`](FINAL_STATE_AUDIT.md) (the completed-system ground-truth audit) ·
demo video: <https://youtu.be/cxYiSkkMOgA>.

> **Status:** the three compliance layers, the seam matrix (Movement 1), the convergence
> result (Movement 2), **all three agents (Movements A/B/C: Red-Team, Triage, Defense) and
> the closed offense↔defense loop**, plus their opt-in **live modes** (LLM-reasoned triage,
> real-Garak red-team, real guarded re-scan — all inside the trust boundary) are built and
> tested; the suite is green. `uv run keystone demo` is the console front door — it runs the
> real arc **entirely within the trust boundary, zero network** (the no-exfiltration proof);
> `make ui` is the Streamlit visual.

## Prerequisites

- **Python 3.12** (and only 3.12 — see `ADR-0001` in `DECISIONS.md`).
- **[`uv`](https://docs.astral.sh/uv/)** as the package manager.
- **A working C/C++ compiler.** NeMo Guardrails pulls in `annoy`, which builds a
  native extension from source. Without a toolchain `uv sync` will fail to build
  it.
  - **Linux:** `sudo apt-get install build-essential`
  - **macOS:** `xcode-select --install` (Xcode Command Line Tools)
  - **Windows:** "Desktop development with C++" workload from the Visual Studio
    Build Tools.

## Setup

```sh
uv python pin 3.12
uv sync --all-groups
uv tool install garak   # isolated CLI, NOT a project dependency
```

## Common commands

```sh
make check   # lint + typecheck + fast tests + audit (the gate; mirrors CI)
make test    # fast tests only
make demo    # the console front door: run the real arc offline (= uv run keystone demo)
make ui      # launch the Streamlit visual app (streamlit run src/keystone/ui/app.py)
```

See `CLAUDE.md` for the full directory map and standing rules.

## Data policy

**Synthetic data only.** No real customer data, no secrets, ever. The
`detect-secrets` pre-commit hook blocks committed credentials.
