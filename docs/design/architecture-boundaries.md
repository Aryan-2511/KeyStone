# Architecture boundaries (the enforced contract)

The dependency rules that keep the **deterministic core** independent of the
**LLM/agent edge**. These are not aspirational prose — they are enforced
mechanically by `import-linter` (wired into `pre-commit` and CI).

See [core-principles.md](./core-principles.md) for the *why* and
[../../ARCHITECTURE.md](../../ARCHITECTURE.md) for the layer map.

## The rule

> The deterministic core (`keystone.core`) must not import the edge layers
> (`keystone.agents`, `keystone.policy`, `keystone.llm`, `keystone.ui`,
> `keystone.assurance`). Dependencies point **inward**, toward the core — never
> outward.

This makes the auditable, reproducible parts of Keystone testable without a
model in the loop.

## The layer packages

All materialized as (currently empty) packages under `src/keystone/`:

| Package | Layer | Depends on core? |
| --- | --- | --- |
| `keystone.core` | Deterministic core (logic, scoring, evidence ledger) | — (lowest) |
| `keystone.llm` | LLM edge (extraction, inference switch) | may |
| `keystone.policy` | NeMo Guardrails rails | may |
| `keystone.agents` | NeMo Agent Toolkit orchestration | may |
| `keystone.assurance` | Garak red-team subprocess driver | may |
| `keystone.ui` | Streamlit front-end | may |

## Enforcement (active)

A `forbidden` contract in `[tool.importlinter]` (`pyproject.toml`) is the source
of truth. It runs in four places:

- `make arch` / `make check` / `make verify` → `uv run lint-imports`
- the `import-linter` **pre-commit** hook
- the **CI** `check` job
- `tests/test_architecture.py::test_import_contract_passes` (programmatic)

On violation, import-linter prints the offending import chain and the contract
name, which states the remediation. **Grow the contract** (e.g. add layered
ordering among the edge packages) as real modules land.
