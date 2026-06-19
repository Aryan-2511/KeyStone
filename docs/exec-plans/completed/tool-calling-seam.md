<!--
Exec-plan (completed). KS-0300 — tool-calling inference seam (deterministic infra).
-->

# Exec-plan: Tool-calling inference seam (KS-0300)

- **Slug:** `tool-calling-seam`
- **Feature IDs:** KS-0300 (Phase 3 / Layer 2 infrastructure). The spike-discovered
  prerequisite the mock agent (KS-0301) `depends_on`. Follows the Ollama/NIM
  tool-calling spike (PR #6).
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-19
- **Owner (session):** agent
- **Branched from:** `main` @ 7f8b4eb (spike merged).

## Why

The spike proved `complete()` cannot tool-call (it sends no tools array), and that
tool-call `arguments` come back differently per backend — a JSON object from
Ollama, a JSON string from NIM. Layer 2's mock agent needs a tool-calling path
that returns one canonical shape regardless of backend.

## What shipped

- `keystone/llm/inference/tools.py`: `ToolCall{name, arguments: dict}`,
  `ToolCallResult{content, tool_calls}` (frozen Pydantic), `normalize_tool_calls()`
  (coerces dict OR JSON-string args → dict; typed `ToolCallNormalizationError` on a
  non-JSON string / malformed payload), and a runtime-checkable `ToolCallingBackend`
  Protocol.
- `OllamaBackend.complete_with_tools` (`/api/chat` + tools, temp 0) and
  `NimBackend.complete_with_tools` (OpenAI `/chat/completions` + tools) — each
  extracts content + raw tool_calls from its own envelope and normalizes via the
  shared helper. The plain `complete()` path is untouched.
- Free `complete_with_tools(messages, tools, *, backend=None)` in `inference/__init__`
  — dispatches to the active backend, raising `InferenceError` if it can't tool-call.
- **Config fix:** default `KEYSTONE_OLLAMA_MODEL` → `qwen2.5:3b` (the spike-chosen,
  actually-pulled model), so the `slow` live roundtrip stops 404ing in `make verify`.
- Tests `tests/test_inference_tools.py`: backend-parity (Ollama-dict and NIM-string →
  identical result), per-backend normalization, text-only → empty list, malformed →
  typed error, unreachable surfaces cleanly, free-fn dispatch + non-tool rejection;
  one live `slow` tool-call per backend that skips cleanly. Fast gate uses mocked
  HTTP — no Ollama, no NIM key.
- **feature_list / numbering:** added **KS-0300** (Phase-3 infra prerequisite); did
  NOT renumber the settled KS-0301–0304. KS-0301 now carries
  `depends_on: ["KS-0300"]`, and `validate_feature_list.py` enforces that
  `depends_on` ids resolve (mechanical, not implied). ADR-0011 amended to record why
  a 0300 appears after 0301–0304 were numbered.

## Decisions

- **Numbering = KS-0300, no renumber** (user decision): the seam precedes the block
  by number; the existing four keep their ids. The prerequisite is structural in the
  data (`depends_on` + validator enforcement), per "mechanical enforcement over prose".
- **status = done** — the seam is implemented, tested, and green. The
  `depends_on` resolution check runs in the FAST gate (via
  `tests/test_feature_list.py`), not just `make verify`.
- Polymorphic `complete_with_tools` per backend (not isinstance branching for
  behaviour) with a shared normalizer; the `Backend` text protocol is unchanged so
  existing `complete()` fakes still type-check.

## Verification

- `make check` green WITHOUT Ollama running / NIM key (parity tests included),
  coverage 93.6%, `tools.py` 100%.
- `make verify` exit 0 — 159 passed / 2 skipped (NIM live, no shell key); live
  Ollama roundtrip + tool-call now pass (default model pulled). import-linter
  core→edge KEPT. `uv run pytest -m slow`: live Ollama tool-call normalizes.

## Next

KS-0301 — the mock vulnerable payments agent, built on this seam (the vulnerability
is designed into the agent's prompt/tool-wiring; see the spike note in MEMORY.md).
