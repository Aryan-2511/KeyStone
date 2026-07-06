# ARCHITECTURE.md

> The three compliance layers, the seam matrix, the convergence result, and the
> **complete three-agent system** (Red-Team + Triage + Defense, with the closed
> offense↔defense loop) are built. This file describes the system as it stands.
>
> Related: [`DECISIONS.md`](DECISIONS.md) (ADR log) ·
> [`docs/design/core-principles.md`](docs/design/core-principles.md) (the *why*) ·
> [`docs/design/architecture-boundaries.md`](docs/design/architecture-boundaries.md)
> (the enforced dependency contract).

## One-line

An orchestrated compliance & assurance system: a NeMo Agent Toolkit workflow
sequences deterministic stages that ingest synthetic artifacts, apply policy via
guardrails, and append verifiable findings to a hash-chained evidence ledger.
Deterministic by design where auditability demands it (FATF detection, the seam,
the ledger) — a feature, not a gap. It is **data-residency-preserving**: all inference
runs local / on-prem so sensitive transaction data + PII never leave the institution's
trust boundary — and the offline console arc, which runs the whole flow with zero
network, is the strongest *proof* of that no-exfiltration path. It is a **complete
multi-agent system**: three genuine agents interacting across the L2↔L1 seam — a **Red-Team
Agent** (offensive worker) that adapts its probe to what landed, a **Triage Agent**
(supervisor) that routes a finding on its signal interplay, and a **Defense Agent** that
chooses which remediation a finding warrants from a genuine ≥2-option menu ({(a) block the
AI-side injection, (c) tighten the money-side detection}) — and the **closed adversarial
loop**: after the Defense Agent patches, the Red-Team RE-SCANS the patched target and adapts
(offense → supervision → defense → re-scan → adapt). Each agent is an observation-driven
policy that clears a strict agency bar (the next action depends on what it observed), NOT an
LLM. Option A (LLM-reasoned decisions) has opt-in live modes (local qwen2.5:3b triage,
real-Garak red-team, both inside the boundary); capable **on-prem** inference is the compute
frontier for making the agents' *decisions* LLM-reasoned (`OPEN_QUESTIONS.md` §B).

## Layers

| Layer            | Responsibility                                         | Determinism |
| ---------------- | ------------------------------------------------------ | ----------- |
| Orchestration    | NeMo Agent Toolkit (`nvidia-nat`) workflow (YAML)      | config      |
| Policy / safety  | NeMo Guardrails (input/output/dialog rails)            | rules       |
| LLM edge         | Extraction, summarization, NL interaction              | LLM         |
| Deterministic core | Compliance logic, scoring, evidence ledger           | pure        |
| Red-team         | Garak (subprocess) probes the deployed surface         | external    |
| Agents           | Red-Team (offense) + Triage (supervisor) + Defense (defender) — observation-driven policies; the offense↔defense loop closes | policy |
| UI               | Streamlit demo front-end                               | n/a         |

The same shape as a diagram — the NeMo Agent Toolkit orchestrator over the three
compliance layers (L3 obligation mapping · L2 AI Assurance with the three agents ·
L1 FATF transaction monitoring), the vulnerable target under test, the seam that binds
an AI exploit to a financial crime, and the shared deterministic spine:

```mermaid
flowchart TD
    ORCH["NeMo Agent Toolkit orchestrator (nvidia-nat workflow)"]

    subgraph L3["L3 - Obligation and control mapping (governance)"]
        OBL["Obligations-to-controls crosswalk; convergence: violated to satisfied"]
    end

    subgraph L2["L2 - AI Assurance: three genuine agents (observation-driven policies, NOT LLMs)"]
        RT["Red-Team Agent (offense: adapts probes to what landed)"]
        TR["Triage Agent (supervisor: routes on signal interplay)"]
        DF["Defense Agent (defender: picks remediation a or c)"]
    end

    subgraph L1["L1 - Transaction Monitor: FATF financial-crime detection (memo-blind)"]
        FATF["FATF typology rules over amounts / timing / accounts"]
    end

    TGT["Target under test: mock-payments-agent (memo-trusting, vulnerable by design)"]
    SEAM{{"The seam: one event is BOTH an AI exploit AND a financial crime"}}

    subgraph SPINE["Shared spine (deterministic, auditable)"]
        GUARD["NeMo Guardrails input rail"]
        BOUND["Memo-blind boundary: detector never reads the attack channel"]
        LEDGER["Hash-chained evidence ledger"]
    end

    ORCH --> L3
    ORCH --> L2
    ORCH --> L1
    L2 -->|"Garak probes the guarded surface"| TGT
    RT -.->|"AI exploit lands"| SEAM
    FATF -.->|"flags STRUCTURING"| SEAM
    SEAM --> SPINE
    L1 --> SPINE
    L3 --> SPINE
```

## Key decisions (see [`DECISIONS.md`](DECISIONS.md))

- Python 3.12 only — [`ADR-0001`](DECISIONS.md#adr-0001--pin-python-to-312-only).
- `uv` for dependency management — [`ADR-0002`](DECISIONS.md#adr-0002--use-uv-for-dependency-management).
- garak isolated as a CLI subprocess — [`ADR-0003`](DECISIONS.md#adr-0003--install-garak-as-an-isolated-cli-subprocess-not-a-dependency).
- pre-commit as a CI gate — [`ADR-0004`](DECISIONS.md#adr-0004--run-pre-commit-incl-detect-secrets-as-a-first-class-ci-gate).

The deterministic-core → edge dependency direction (LLM edge must not be
imported by the core) is enforced mechanically; see
[`docs/design/architecture-boundaries.md`](docs/design/architecture-boundaries.md).

## Inference switch

A single config toggle selects the inference backend on one code path:

- **Hosted NIM** → demo mode (no local GPU needed).
- **Local Ollama** → production mode.

## Evidence ledger

Append-only, hash-chained records (each entry commits to the prior entry's
hash) backed by SQLite — a tamper-evident audit trail. Implemented in
`keystone.core.ledger` (KS-0102/0103).

## Data flow

Synthetic artifacts → deterministic detection (FATF) → the seam binds detection to
reporting across a memo-blind boundary → obligation/control mapping → the **Red-Team
Agent** probes the guarded surface, the **Triage Agent** routes the finding, the **Defense
Agent** chooses + applies a remediation, and the **Red-Team re-scans the patched target and
adapts** (the closed offense↔defense loop) → every step appends to the hash-chained ledger.
The convergence view shows a seam event taking named obligations from *violated* to
*satisfied*. One run is reachable three ways over the same arc: `keystone demo` (console
front door, `make demo`), the Streamlit app (`make ui`), and `python -m keystone.demo`
(build + save a run-result). The console narration walks all of it, ending on the loop
finale ("4c. Adversarial loop — offense re-tests defense").

## The seam (the thesis)

The load-bearing claim: **one event is both an AI-security failure and a financial crime**,
bound on the shared transaction id — and the two detections are held *independent* by the
memo-blind boundary (the FATF detector never reads the attack channel), which is what keeps
the convergence result trustworthy rather than circular.

```mermaid
flowchart LR
    RTX["AI-security side (L2): Red-Team Agent finds a memo prompt-injection (latentinjection, OWASP LLM01)"]
    FATFX["Financial-crime side (L1): FATF flags STRUCTURING from financial signals only (amounts / timing / accounts)"]
    TX{{"ONE event: transaction TXN-000016"}}
    BOUND["Memo-blind boundary: the FATF detector NEVER reads the attack channel (the memo)"]
    THESIS["The seam thesis: the same event is BOTH an AI-security failure AND a financial crime, bound on the shared tx id"]

    RTX -->|"AI-security failure"| TX
    FATFX -->|"financial crime"| TX
    BOUND -.->|"structural independence: the two detections cannot be circular"| FATFX
    TX --> THESIS
```

## The multi-agent adversarial loop

The finale: after the Defense Agent patches, the Red-Team **re-scans the patched target** and
adapts — the closed offense↔defense loop (offense → supervision → defense → re-scan → adapt).
All three agents are observation-driven policies, not LLMs; the core stays deterministic; the
agents choose, humans govern.

```mermaid
flowchart TD
    RT["Red-Team Agent: fires a probe; an exploit LANDS (measured 11/12)"]
    TR["Triage Agent: routes the finding by signal interplay (remediate / accept / escalate)"]
    DF["Defense Agent: chooses a remediation by two-sided strength -- (a) block the AI-side injection at the guardrail, or (c) tighten the money-side FATF detection"]
    RESCAN["Re-scan the PATCHED target: does the exploit still land? (measured 11/12 unpatched, then 0/12 once the rail is on)"]
    NOTE["Honest framing: all three agents are observation-driven policies (NOT LLMs); the core is deterministic; the agent chooses, humans govern"]

    RT --> TR
    TR --> DF
    DF --> RESCAN
    RESCAN -->|"the Red-Team ADAPTS to the patch: abandons a closed surface, or pivots to an open family"| RT
    NOTE -.-> DF
```
