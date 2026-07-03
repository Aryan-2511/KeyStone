# Core principles

The standing doctrine for Keystone. `CLAUDE.md` links here; this file holds the
*why*. Two parts: **domain principles** (how the system is built) and **golden
principles** (how agents work in this repo).

---

## Domain principles

### Data-residency-preserving (no exfiltration)
The load-bearing requirement in regulated finance is **data residency**: sensitive
transaction data and PII must never leave the institution's **trust boundary** to a
third-party API. So **all inference runs local / on-prem** — the sensitive data stays
inside the boundary, always. "Offline" is not the goal in itself; it is the *proof* of
the no-exfiltration path, and the **strongest** form of it: the console arc runs the
whole assurance flow with **zero network**, which is a guarantee no cloud-API system can
make, not a limitation. The compute frontier (capable models for LLM-reasoned decisions,
`OPEN_QUESTIONS.md` §B) is therefore an ask for **on-prem NVIDIA inference (NIM inside the
trust boundary)** — capable models *without data leaving* — never "more internet". This is
a framing of what is already built (the architecture runs inference locally); on-prem NIM
is a design target, not a deployed component.

### Deterministic core / LLM edge
Business logic, the evidence ledger, and policy decisions are **deterministic
and testable**. LLMs live only at the edges — extraction, summarization, natural
-language interaction. Anything that must be auditable or reproducible does not
depend on a model's output. This boundary is enforced mechanically; see
[architecture boundaries](./architecture-boundaries.md).

### Synthetic data only
Fixtures, examples, and demos use **synthetic data exclusively**. No real
customer data, no secrets, ever. The `detect-secrets` hook (now a CI gate, see
`ADR-0004`) blocks committed credentials.

### Inference is a config switch
The inference backend is selected by configuration on **one code path** — and every
option keeps inference **inside the trust boundary** (the data-residency principle above):
- **Local Ollama** → the default; runs on-prem, no data leaves.
- **On-prem NIM** → the capability target: NVIDIA-hosted inference deployed *inside* the
  institution's boundary, for capable models without exfiltration (a design target, not
  yet deployed).

Same code, different config — never a forked code path per backend, and never a
third-party API that would send sensitive data outside the boundary.

### Hash-chained evidence ledger
Every assurance event is appended to a tamper-evident, **hash-chained** ledger
(each entry commits to the prior entry's hash), backed by SQLite. The audit
trail is independently verifiable. _Design lands in a later phase._

---

## Golden principles (for agents)

These map to the three reference philosophies the harness is built on.

1. **Repository is the system of record.** If an agent cannot read it in-repo,
   it does not exist. Knowledge lives in versioned, cross-linked docs.
2. **Progressive disclosure.** `CLAUDE.md` is a *map*, not an encyclopedia.
   Depth lives in `docs/`. Read the pointer for your task, not the whole tree.
3. **Mechanical enforcement over prose.** If a rule can be a linter, a
   structural test, or a CI check, make it one. Prose rules rot; checks don't.
4. **Generator/evaluator separation.** Verification is a separate, skeptical
   step (`make verify`) that fails loudly rather than rationalizing gaps. Do not
   grade your own work leniently.
5. **Structured handoff survives resets.** State that must outlive a session
   goes into an [exec-plan](../exec-plans/), not into chat or model memory.
6. **Simplest thing that works.** Every harness component encodes an assumption
   about what the model can't do alone. Don't add one unless it earns its place;
   flag premature components as explicit *deferred*, not silent omissions.

---

## Non-negotiables (the hard constraints)

Mirrored tersely in `CLAUDE.md`; full rationale in `../../DECISIONS.md`.

- **Python 3.12 only** (`>=3.12,<3.13`). See `ADR-0001`.
- **`uv` is the only package manager**; commit `uv.lock`. See `ADR-0002`.
- **`garak` is not a project dependency** — isolated CLI, called as a
  subprocess. See `ADR-0003`.
- **Strict gates, never weakened.** mypy `strict`, Ruff security rules,
  `--cov-fail-under` floor. Fix the code or ask — never relax a gate, never add a
  blanket `# type: ignore` / `noqa` to go green.
- **Synthetic data only.** No real data, no secrets.
- **Out of scope:** Docker, tox, Sphinx, multi-version CI matrices.
