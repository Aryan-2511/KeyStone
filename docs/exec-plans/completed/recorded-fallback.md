<!--
Exec-plan (completed). KS-0504 — recorded-run fallback (the demo safety net).
A fully-offline, deterministic recorded run the UI replays, indistinguishable from live.
-->

# Exec-plan: recorded-run fallback (KS-0504)

- **Slug:** `recorded-fallback`
- **Feature IDs:** KS-0504 (Phase 5 / Integration & demo). `depends_on` KS-0500/0503.
- **Status:** done (PR open; not self-merged)
- **Started:** 2026-06-22
- **Owner (session):** agent
- **Branched from:** `main` @ d17297d (KS-0503 merged).

## Why

Demo insurance: if live fails on stage (no wifi / cold GPU / flaky box), one switch
plays a recorded run that looks EXACTLY like live — same five views, real values,
instant, fully offline. Success = the fallback is reliable, zero-dependency, the safe
default, and visually identical to live. Mostly hardening the replay KS-0500/0502
already enabled.

## What shipped

- **The canonical recording, promoted out of tests/fixtures.**
  `src/keystone/demo/recorded_run.json` — a genuinely-produced v3 `build_run_result`
  output (saved via `python -m keystone.demo`, never hand-edited). One source of truth,
  exposed by `keystone.demo.recorded_run_path()` / `load_recorded_run()`. The old
  `tests/fixtures/seam_run_result.json` was deleted and all 9 references (3 apps + 6
  test files) repointed to the helper.
- **Offline guarantee** — `tests/test_offline_fallback.py`: blocks
  `socket.connect`/`create_connection`/`getaddrinfo`, then loads the recording and
  renders ALL FIVE views — proving the replay path makes zero network/Ollama/GPU calls.
  Plus: v3 + chain-valid offline, round-trips, and matches a fresh build on substantive
  values (genuine, not fabricated).
- **Recorded is the SAFE DEFAULT** — the shell's Data source defaults to "Replay saved
  run" (the recording); flip to "Live run" to build on stage (also offline). All three
  apps default their replay path to the recording (a stray `keystone-run.json` no
  longer overrides it). A test asserts the shell's default is replay.
- detect-secrets exclude extended to the new recording path (synthetic ledger hashes).
- Review artifact (recorded mode, from the running shell):
  `docs/assets/ks-0504-recorded-mode.png`.

![Shell in recorded mode (safe default)](../../assets/ks-0504-recorded-mode.png)

## Decisions

- **Data replay through the real UI, not a video.** The fallback is the actual app,
  just offline — better than a lossy screen-recording, and the screens are the real
  ones rendering real values.
- **Promote to a package-owned artifact.** The recording lives in the package with a
  helper, so it's one source of truth used by BOTH the demo and the tests (the tests
  validate the actual recording — it can't rot).
- **Honest offline scope.** The Python replay path is provably zero-socket. The only
  network touch is the browser's optional Google-Fonts `@import`, which falls back to
  system fonts offline and affects live + recorded equally (still indistinguishable).
  Documented, not hidden; not gold-plated by embedding fonts.

## Verification

- `make check` + `make verify` green (300 passed); mypy strict, Ruff, import-linter KEPT.
- **Offline test** passes with all outbound sockets blocked — the guarantee this task
  exists for.
- **Visual QA** — `uv run streamlit run src/keystone/ui/shell_app.py` opens in recorded
  mode by default; captured the recorded-mode shell rendering the heroes + supporting
  views, identical to the live captures from KS-0503.

## Next

KS-0505 — demo script + rehearsal (the narrated walkthrough seam → jurisdiction →
shell), using this recorded run as the rehearsal/offline default.
