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

## Honesty probes (committed, in-repo)

| Artifact | Location | What it is / purpose |
| --- | --- | --- |
| Agentic audit | [`agentic_audit.md`](agentic_audit.md) | The probe that asked, honestly, whether anything here was really an agent — the origin of the "policy, not LLM" discipline. |
| Multi-agent feasibility | [`multi_agent_feasibility.md`](multi_agent_feasibility.md) | The probe assessing whether a genuine second agent (→ multi-agent) was warranted, and how. |

## Governance & audit (committed, in-repo)

| Artifact | Location | What it is / purpose |
| --- | --- | --- |
| Ground-truth audit | [`CONSOLIDATION_AUDIT.md`](CONSOLIDATION_AUDIT.md) | This consolidation's read-only audit: every fact CONFIRMED (with cite) or UNCLEAR (with reason). |
| Open questions | [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md) | The honest loose-ends list: unverifiable facts + deferred implementation. |
| Decision log | [`DECISIONS.md`](DECISIONS.md) | ADRs — the load-bearing decisions and their rationale (incl. ADR-0015–0020 from this consolidation). |
| Architecture | [`ARCHITECTURE.md`](ARCHITECTURE.md) | Layers, boundaries, data flow. |
| Roadmap / tasks | [`ROADMAP.md`](ROADMAP.md) · [`TASKS.md`](TASKS.md) | Human-readable phase/task view; source of truth is `docs/feature_list.json`. |
| Design figures | `docs/assets/` | The rendered hero figures (seam, jurisdiction, convergence, matrix, agents). |
