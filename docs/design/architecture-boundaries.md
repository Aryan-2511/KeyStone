# Architecture boundaries (the enforced contract)

The dependency rules that keep the **deterministic core** independent of the
**LLM/agent edge**. These are not aspirational prose — they are enforced
mechanically by `import-linter` (wired into `pre-commit` and CI).

See [core-principles.md](./core-principles.md) for the *why* and
[../../ARCHITECTURE.md](../../ARCHITECTURE.md) for the layer map.

## The rule

> The deterministic core must not import the agent, guardrails, or LLM-edge
> layers. Dependencies point **inward**, toward the core — never outward.

This makes the auditable, reproducible parts of Keystone testable without a
model in the loop.

## Status

> **Phase 1:** stub. The contract and the empty layer packages are materialized
> in the architecture-enforcement phase (see `ROADMAP.md`). The
> `importlinter` config in `pyproject.toml` is the source of truth once active.

_The concrete contract (layers, allowed/forbidden imports) is filled in when the
packages are created._
