<!--
Exec-plan. Keep it current AS YOU WORK — handoff for any future session.
On completion run the verify gate and move to docs/exec-plans/completed/.
-->

# Exec-plan: Resolve transitive cryptography CVE (GHSA-537c-gmf6-5ccf)

- **Slug:** `dependency-hygiene-cryptography`
- **Feature IDs:** none (dependency hygiene; pre-existing on `main`, split off
  from the KS-0201 obligation-graph work).
- **Status:** done (archived 2026-06-17)
- **Started:** 2026-06-17
- **Owner (session):** agent

## Goal & acceptance

`make verify` is red ONLY because `pip-audit` flags transitive `cryptography`
**46.0.7** (GHSA-537c-gmf6-5ccf, advisory range: introduced 0.5.0, **fixed
48.0.1** — single fix, no patched line below 48). Acceptance = `make verify`
fully green again WITHOUT weakening a gate (CLAUDE.md non-negotiable), or a
user-signed-off, time-boxed, documented exception if no clean fix exists.

## Context / constraints

- I introduced no dependencies — `git diff uv.lock` is empty — so this CVE
  predates KS-0201 and exists on `main` independently.
- `cryptography` is transitive: required by `nvidia-nat-core`, `authlib`,
  `joserfc`. `authlib`/`joserfc` accept ≥48 (tested: resolve to 49.0.0). The
  binding cap is **`nvidia-nat-core`** → `cryptography<47,>=46.0.6`.
- CLAUDE.md: strict gates never weakened; record dep changes as an ADR;
  `garak`-style isolation does not apply here.

## Investigation (read current PyPI metadata — do not assume versions)

### (1) Does any `nvidia-nat ≥1.7` bump free cryptography to ≥48? — NO.

- Latest **stable** `nvidia-nat` / `nvidia-nat-core` = **1.7.0** (our current
  pin). Everything newer on PyPI is a prerelease (1.8.0rcN, 1.9.0aN).
- `nat-core` `cryptography` requirement by version (from PyPI JSON):
  - 1.6.0 → *(none declared)*
  - 1.7.0 → `cryptography<47,>=46.0.6`
  - 1.8.0rc7 → `cryptography<47,>=46.0.6`
  - 1.9.0a (latest) → `cryptography<47,>=46.0.6`
- The cap persists through the newest prereleases. The only cap-free version is
  the OLDER 1.6.0 — a downgrade, not a bump, and no patched cryptography exists
  below 48 anyway. **Option (1) exhausted.**

### (2) `[tool.uv]` override forcing cryptography ≥48 + run the gate — GREEN.

- Added `[tool.uv] override-dependencies = ["cryptography>=48.0.1"]`, re-locked,
  synced → cryptography resolved to **49.0.0** (latest; > advisory fix 48.0.1).
- **`make check`**: PASS — lint, mypy strict, import-linter arch, 52 passed
  (1 deselected milestone), and `pip-audit` → **"No known vulnerabilities found."**
- **Full `make verify`**: PASS — `52 passed, 1 skipped`, including the chassis
  milestone `test_chassis_runs_three_layers_and_chain_verifies` (exercises the
  NAT workflow API), `pip-audit` clean → `"verify: acceptance gate passed"`.
- **Conclusion:** nat-core's `cryptography<47` cap is a conservative upper bound,
  NOT a guard against a real break in our usage. The override is a clean fix.
- Experiment **reverted** (`git checkout -- pyproject.toml uv.lock`, re-synced to
  46.0.7) pending user sign-off before any permanent pin change.

### (3) Time-boxed documented `pip-audit` exception — _last resort, needs sign-off_

- Only if (2) shows a real nat-core break. Would require a removal trigger
  (e.g. "drop when nvidia-nat releases a stable line allowing cryptography≥48")
  and explicit user sign-off. NOT to be applied unilaterally.

## Progress log

- 2026-06-17 created plan. Confirmed option (1) fails via PyPI metadata; advisory
  fix is 48.0.1 only. Ran option-(2) override test → full gate green; reverted.
- 2026-06-17 user signed off on option (2). Adopted `[tool.uv]` override, wrote
  ADR-0013 (+ index row), re-locked/synced (cryptography 49.0.0), `make verify`
  green. Plan complete.

## Decisions

- **Adopted the `[tool.uv]` override → ADR-0013.** `override-dependencies =
  ["cryptography>=48.0.1"]` in `pyproject.toml`. Security override, not a gate
  relaxation — `pip-audit` stays strict and now passes. Removal trigger: drop
  when a stable `nvidia-nat` allows `cryptography>=48` (re-check `nat-core`
  `requires_dist` on the next bump).

## Open questions / blockers

- None. Resolved.

## Next steps (resume here)

Nothing — task complete. Watch for the removal trigger on future `nvidia-nat`
bumps (ADR-0013).

## Handoff

- **What changed:** `pyproject.toml` `[tool.uv] override-dependencies =
  ["cryptography>=48.0.1"]`; `uv.lock` re-resolved (cryptography 46.0.7 → 49.0.0);
  ADR-0013 added to `DECISIONS.md` (+ index row).
- **Verified:** `make verify` → `"verify: acceptance gate passed"`, `pip-audit`
  → "No known vulnerabilities found", full suite incl. chassis milestone green.
- **Deferred:** none. Removal trigger tracked in ADR-0013.
- **Recommended next task:** KS-0205 (citation-validation gate) per the
  obligation-graph handoff.
