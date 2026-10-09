# Testing & logging policy - C:\Projects

One mindset, applied per project. Every project is standalone - the
convention is shared, the code is not. Built 2026-10-09; the rollout's
rationale and open questions are in `.agent_tasks/test-suite-rollout/`.

## Running tests

```
python run_all_tests.py            # every project, summary table at the end
python run_all_tests.py --quick    # skip tests marked @slow / network
cd <project> && python run_tests.py        # one project
cd <project> && python -m unittest discover -s tests -v   # raw unittest
cd <project> && python -m pytest tests/ -x -q             # optional richer runner
```

pytest 9 is installed machine-wide and collects every `unittest.TestCase`
unchanged - use it for assertion diffs, `-k` filtering and `--lf`
(re-run failures). Suites stay unittest-style on purpose: the
zero-dependency `run_tests.py` path keeps working on a fresh machine.

Run before commits/pushes and after any major change. A red suite means the
change or the environment broke something - read the log, do not assume the
test is wrong (several projects document "the harness was the bug" traps;
check the stimulus first, then the code).

## What lives where

| Piece | Location |
|---|---|
| Tests | `<project>/tests/test_*.py` - stdlib `unittest`, no third-party test deps |
| Runner | `<project>/run_tests.py` - discovery + UTF-8 log + exit code |
| Test output | `<project>/logs/test-<timestamp>.log` (UTF-8; console is cp1252) |
| App logs | `<project>/logs/<app>.log` via `RotatingFileHandler` |
| Orchestrator | `C:\Projects\run_all_tests.py` |
| Log monitor | `project-hub` Storage table (`/api/storage`) |

## Test layers, cheapest first

1. **Unit** - pure functions, parsing, invariants. Fixtures live in the test
   file or `tests/fixtures/`; never read `data/` (private and mutable).
2. **Regression** - golden invariants the project already documented
   (e.g. chrome-bookmarks' checksum derivation, disk-cleanup's rollup
   invariant, money-plan's `analyze.py --check`).
3. **Smoke** - web apps are spawned on an alternate port and hit with real
   HTTP: status codes, JSON shape, key HTML markers. Loopback only.
4. **DOM/render** - where it exists: disk-cleanup's `test_render.js`
   (Node VM + stubbed DOM against the live server). Add views to its `cases`
   list when adding views.
5. **Perf** - wall-clock budgets inside smoke tests (generous, e.g. an
   endpoint must answer < 2 s). They catch order-of-magnitude regressions.
6. **Browser** - real headless Chromium via Playwright (installed
   machine-wide, browsers included). Each serving project has
   `tests/test_browser.py`: spawn the app on an alternate port, load the
   page for real, exercise one read-only control, and fail on any uncaught
   JS error (`pageerror`/`console.error`, network noise filtered). Skips
   cleanly when playwright or its binaries are absent
   (`python -m playwright install chromium`) and under `--quick`.
   money-plan runs its handler in-process over a fixture store - real
   private data is never loaded in a test browser.

Tests that need hardware, credentials, network or missing deps must
`unittest.skipUnless`/`skipTest` rather than fail.

## Logging policy

- **Where:** `<project>/logs/` - always gitignored, never in `data/` unless
  the log *is* the data product (nirvana's scrape.log).
- **How:** stdlib `logging`, `RotatingFileHandler`, UTF-8, default cap
  `LOG_MAX_BYTES = 1 MB`, `LOG_BACKUPS = 5` (~6 MB per app worst case).
- **Console:** stdout/stderr reconfigured with `backslashreplace` where the
  app prints data it did not author (cp1252 trap).
- **Retention:** rotation is the deletion policy - no manual sweeping needed.
  The project-hub Logs & Disk panel shows per-service log sizes and C: free
  space so growth is visible before it becomes a problem.
- **What gets logged:** startup, binds/ports, request errors with tracebacks,
  state transitions (start/stop/capture), and warnings - not request bodies
  or private payloads.

## Adding a test

New behaviour = new test in the same commit. A bug found by testing gets a
regression test pinning the fix before the fix lands, when practical.
