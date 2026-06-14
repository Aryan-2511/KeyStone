# MEMORY.md — durable project facts

> Facts that are NOT derivable from the code or git history. One line each.
> (This is the project's own memory file, distinct from any agent memory store.)

- Python is pinned to **3.12 only** — verified intersection of nvidia-nat,
  nemoguardrails, and garak. Re-validate before bumping. (ADR-0001)
- **garak is intentionally absent from `pyproject.toml`** — it lives as an
  isolated `uv tool` and is called as a subprocess. Don't "fix" its missing-dep
  by adding it. (ADR-0003)
- The `keystone` console script and `make demo` are **Phase 0 placeholders** —
  no real CLI/demo wiring exists yet.
- Resolution fact (2026-06-14): `nvidia-nat` + `nemoguardrails` resolve together
  cleanly under 3.12 with `uv`; no hand-edited pins were needed.
- `annoy` (a Guardrails dependency) builds a native extension — a C/C++ compiler
  is a hard install prerequisite.
