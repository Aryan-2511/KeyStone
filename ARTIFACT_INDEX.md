# ARTIFACT_INDEX.md — every external artifact, and where it lives

> One table for a mentor/judge to find everything: the submission artifacts, the
> design records, the honesty probes, and this consolidation's audit. **Committed**
> rows link relatively (in-repo). **External / not committed** rows are plain text
> on purpose — a dead relative link would fail
> `tests/test_docs.py::test_no_broken_relative_links`. See
> [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md) §A5 for the absent-artifact decision.

## Submission / presentation artifacts

| Artifact | Location | What it is / purpose |
| --- | --- | --- |
| Pitch deck | `BigBird-Presentation.pptx` — **external, not committed** | The hackathon deck: problem-first framing, the buyer-split, the seam thesis. Source of the "10 instruments / 3 jurisdictions" breadth claim the repo does not encode (see `OPEN_QUESTIONS.md` §A1). |
| Demo video | <https://youtu.be/cxYiSkkMOgA> — **external (hosted)** | The recorded walkthrough of the demo. Not referenced by any committed repo doc; pointer supplied by the submission. |
| Infographic ×2 | **external, not committed** | The two supporting infographics from the submission. |
| Demo script | **external, not committed** | The narration/run-order for the demo. |
| `KEYSTONE_REGULATORY_REFERENCE.md` | **external, not committed** | The regulatory-reference companion. The repo's own encoded truth is `src/keystone/core/obligations/data/obligations.json` (28 obligations, 6 instruments, 2 jurisdictions). |
| `KNOWLEDGE_BASE` | **external, not committed** | Background knowledge base. |
| `RESEARCH_AND_NOVELTY` | **external, not committed** | The research / novelty write-up. |

## Design records (committed, in-repo)

| Artifact | Location | What it is / purpose |
| --- | --- | --- |
| Movement 1 — seam matrix design | [`M1-00_SEAM_MATRIX_DESIGN.md`](M1-00_SEAM_MATRIX_DESIGN.md) | The seam-pair matrix design (the 5 registered pairs: 4 CLEAN + 1 BOUNDARY). |
| Movement 2 — convergence design | [`M2-00_CONVERGENCE_DESIGN.md`](M2-00_CONVERGENCE_DESIGN.md) | The convergence result design (10/12 → 0/12; the REGISTERED_MAPPINGS). |
| Movement A — Red-Team Agent design | [`MA-00_REDTEAM_AGENT_DESIGN.md`](MA-00_REDTEAM_AGENT_DESIGN.md) | The offensive agent design, incl. the §2 honesty bar and Option A/B split. |
| Movement B — Triage Agent design | [`MB-00_TRIAGE_AGENT_DESIGN.md`](MB-00_TRIAGE_AGENT_DESIGN.md) | The supervisory triage-agent design, incl. the §2 interplay bar. |
| Movement C — Defense Agent design | [`MC-00_DEFENSE_AGENT_DESIGN.md`](MC-00_DEFENSE_AGENT_DESIGN.md) | The defender design: the uniform remediation interface, the finding-dependent choice, and the adversarial loop (MC-01 built the agent, MC-02 closed the loop). |
| Option A — live Triage design | [`OPTION-A-00_TRIAGE_LIVE_DESIGN.md`](OPTION-A-00_TRIAGE_LIVE_DESIGN.md) | The opt-in live-LLM Triage design (qwen2.5:3b, policy fallback, honest reasoner tag). |
| Option A — live Red-Team design | [`OPTION-A-02-00_REDTEAM_LIVE_DESIGN.md`](OPTION-A-02-00_REDTEAM_LIVE_DESIGN.md) | The opt-in real-Garak Red-Team design (recorded-profile fallback, source tag, cost discipline). |

## Honesty probes (committed, in-repo)

| Artifact | Location | What it is / purpose |
| --- | --- | --- |
| Agentic audit | [`agentic_audit.md`](agentic_audit.md) | The probe that asked, honestly, whether anything here was really an agent — the origin of the "policy, not LLM" discipline. |
| Multi-agent feasibility | [`multi_agent_feasibility.md`](multi_agent_feasibility.md) | The probe assessing whether a genuine second agent (→ multi-agent) was warranted, and how. |
| Remediation-menu probe | [`remediation_probe.md`](remediation_probe.md) | The MENU-FIRST probe: whether a genuine ≥2-option remediation menu exists (gating the Defense Agent) — the origin of remediation (c) and the finding-dependent choice. |

## Governance & audit (committed, in-repo)

| Artifact | Location | What it is / purpose |
| --- | --- | --- |
| Final-state audit | [`FINAL_STATE_AUDIT.md`](FINAL_STATE_AUDIT.md) | The **completed-system** read-only audit (three agents + closed loop): every item CLEAN / STALE / MESSY / UNCLEAR with a cite. Supersedes the earlier snapshot below. |
| Earlier ground-truth audit | [`CONSOLIDATION_AUDIT.md`](CONSOLIDATION_AUDIT.md) | An earlier consolidation's read-only audit (kept as history): every fact CONFIRMED (with cite) or UNCLEAR (with reason). |
| Open questions | [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md) | The honest loose-ends list: unverifiable facts + deferred implementation. |
| Decision log | [`DECISIONS.md`](DECISIONS.md) | ADRs — the load-bearing decisions and their rationale (ADR-0001–0030, incl. the Movement A/B/C agent decisions ADR-0015–0022, 0026, 0028–0030). |
| Architecture | [`ARCHITECTURE.md`](ARCHITECTURE.md) | Layers, boundaries, data flow. |
| Roadmap / tasks | [`ROADMAP.md`](ROADMAP.md) · [`TASKS.md`](TASKS.md) | Human-readable phase/task view; source of truth is `docs/feature_list.json`. |
| Design figures | `docs/assets/` | The rendered hero figures (seam, jurisdiction, convergence, matrix, agents). |
