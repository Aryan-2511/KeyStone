# Keystone

An **orchestrated compliance & assurance** demo built on the NVIDIA agentic
stack — [NeMo Agent Toolkit](https://github.com/NVIDIA/NeMo-Agent-Toolkit)
(`nvidia-nat`) for orchestration, [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
for policy, and [Garak](https://github.com/NVIDIA/garak) for red-teaming.
**Deterministic by design** where auditability demands it (FATF detection, the seam
binding, the hash-chained ledger) — that determinism is a feature, not a gap — and
now a **multi-agent system**: two genuine agents in a supervisor–worker topology —
an offensive **Red-Team Agent** and a supervisory **Triage Agent** — each reasoning
through an explicit, observation-driven policy (not an LLM; "LLM-reasoned" is a
named later upgrade, Option A). They are agents by a strict bar: the next action
demonstrably depends on what they observed.

## Start here (for reviewers)

**What Keystone is.** A demo of *orchestrated compliance & assurance* for
financial-sector AI: it maps regulatory obligations to a unified control spine,
detects a risk once and renders it into every regulator's report format, red-teams
the guarded surface, and writes tamper-evident evidence to a hash-chained ledger —
deterministic where auditability demands it, with two genuine agents at the edge.

**The two agents.** A **Red-Team Agent** (offensive worker) adapts its next
prompt-injection probe to what the last one revealed; a **Triage Agent**
(supervisor) routes each finding — remediate / accept / escalate — on the
*interplay* of its signals, not a single threshold. Both are observation-driven
policies, framed honestly as such.

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
stay the default; capable **on-prem** inference is the evidence-backed compute frontier.
Movement C (a defense agent, gated on a real ≥2-remedy menu) and Movement 3 (adversarial
self-testing) are deferred.

**Run it (from a clean clone).** After [Setup](#setup) below:

```sh
uv run keystone demo   # runs the real arc end to end within the trust boundary — no data leaves; no Ollama/Garak/network needed
```

This runs one genuine Layer-1 assurance arc and narrates the actual result it
produced: the FATF finding, the Red-Team Agent's landed exploit, the seam bind,
the Triage Agent's route, and the sealed hash-chained ledger. It is deterministic
and runs with **zero network** — the strongest proof of the **data-residency /
no-exfiltration** guarantee the product is built for (sensitive data never leaves the
institution's trust boundary; all inference is local / on-prem). `make demo` is the
same command; `make ui` opens the visual Streamlit version. An opt-in `--live` mode
takes the two agents live *inside the boundary* (real Garak scans, local-LLM triage).

**Where to look:** [`ARCHITECTURE.md`](ARCHITECTURE.md) (layers & boundaries) ·
[`DECISIONS.md`](DECISIONS.md) (the load-bearing *why*) ·
[`ARTIFACT_INDEX.md`](ARTIFACT_INDEX.md) (deck, demo video, design docs, probes) ·
[`CONSOLIDATION_AUDIT.md`](CONSOLIDATION_AUDIT.md) (ground-truth audit) ·
demo video: <https://youtu.be/cxYiSkkMOgA>.

> **Status:** the three compliance layers, the seam matrix (Movement 1), the
> convergence result (Movement 2), both agents (Movements A/B), and their opt-in **live
> modes** (LLM-reasoned triage, real-Garak red-team — both inside the trust boundary)
> are built and tested; the suite is green. `uv run keystone demo` is the console front
> door — it runs the real arc **entirely within the trust boundary, zero network** (the
> no-exfiltration proof); `make ui` is the Streamlit visual.

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
