# Task: test-suite-rollout

Status: in progress
Started: 2026-10-09 (overnight run, user asleep - no blocking questions; see
DECISIONS.md for calls that were made and calls left open)

## Objective

Give every project in `C:\Projects` a unit + regression test suite that runs
before commits/pushes, a consistent logging approach (rotating, size-capped),
a log-retention policy enforced/monitored via `project-hub`, and push every
repo to `github.com/jovandrei-projects`. Fix bugs the tests reveal.

## Hard constraints

- **money-plan is touched LAST.** Another agent is editing it (app.py mtime
  was the current minute at session start). Only start once no file under
  `C:\Projects\money-plan` has been modified in >= 60 minutes. Re-check at
  that point; if still dirty, leave it and record in this file.
- **singing-practice-tools has ~31 files modified by earlier work** (user may
  be evaluating them). Write tests, run them, but `git add` ONLY new files
  this rollout created (`tests/`, `run_tests.py`, AGENTS.md edits). Never
  commit the pre-existing modifications.
- Stdlib `unittest` only for Python tests - machine rule is stdlib-only and
  the user cannot approve new dependencies overnight. video-tools has a venv;
  singing-practice-tools has requirements.txt - tests there may use installed
  deps but must `unittest.skipUnless` on import failure.
- Tests must never touch real private data: fixtures only. wifi-monitor,
  chrome-bookmarks, money-plan hold private data.
- cp1252 console trap: test runners must configure stdout with
  `backslashreplace` and write full output to UTF-8 files.

## The design (read DECISIONS.md for rationale)

- Each project: `tests/` (unittest `TestCase`s), `run_tests.py` (thin
  wrapper: discover + UTF-8 log to `logs/test-*.log` + exit code),
  `logs/` gitignored, AGENTS.md gains a *Testing* section.
- Servers also get an app log: stdlib `logging` + `RotatingFileHandler`
  writing `logs/<project>.log` (1 MB x 5 backups default policy).
- `C:\Projects\run_all_tests.py` - orchestrator: runs each project's
  `run_tests.py` in sequence, prints a summary table, writes
  `logs/test-run-<ts>.log`, nonzero exit if any project fails.
- `project-hub` gains a Logs & Disk panel: per-service log size, per-project
  `logs/` total, C: free space, warn colors over thresholds.
- Selenium-style layer = HTTP smoke tests + disk-cleanup's existing
  `test_render.js` Node-DOM approach as the pattern. Real Selenium needs
  deps - left as an open decision in DECISIONS.md.
- Performance layer = generous time budgets asserted inside smoke tests
  (`test_perf.py` where worthwhile), not a benchmark suite.

## Phases / checklist

Phase 0 - meta + docs
- [x] Inventory all projects, remotes, dirty state
- [x] Write this STATE.md + DECISIONS.md + root TESTING.md
- [x] Root .gitignore: add missing project dirs, /nul, /logs/
- [x] Delete junk `nul` file
- [x] Commit projects-meta (AGENTS.md was already modified by earlier work -
      review it, it indexes money-plan/senior-safety-mx/favicon rule)

Phase 1 - per-project suites (order = least risky first)
- [x] chrome-bookmarks
- [x] model-compare
- [x] nirvana-concert-images
- [x] senior-safety-mx  (created private remote)
- [x] thermalwatch
- [x] disk-cleanup  (wrapped existing test_render.js via live-server test)
- [x] wifi-network-monitor  (needed a main() guard so it imports cleanly)
- [x] video-tools  (created private remote)
- [x] project-hub  (tests + /api/storage log/disk panel landed)
- [x] singing-practice-tools  (run_tests.py wraps existing gate; see notes)

Phase 2 - the guarded one
- [x] money-plan: quiet since the 02:30 commit (~70 min at start). Tests
      patch store/inbox to temp dirs - no real data touched. Private remote
      created, pushed.

Phase 3 - wrap-up
- [x] run_all_tests.py green across every project that has tests
      (10/11; singing-practice-tools red = documented in-flight manifest
      rename, not a rollout defect)
- [x] Update root AGENTS.md: testing/logging policy pointer + TESTING.md
- [x] Push every repo incl. projects-meta
- [x] Final STATE.md update + per-project efficiency_stats.md rows

## Per-project notes (fill in as phases land)

| Project | Suite | Result | Commit |
|---|---|---|---|
| chrome-bookmarks | tests/ (3 files) + run_tests.py | 40/40 | ec6cdb6 |
| model-compare | tests/ (3 files) + run_tests.py | 35/35 | 503b0cd |
| nirvana-concert-images | tests/test_scrape.py | 24/24 | df52323 |
| senior-safety-mx | tests/ (2 files) | 21/21; suite caught empty price row on apple-watch, fixed | fe2dc1d (new private repo) |
| thermalwatch | tests/ (2 files) + run_tests.py | 25/25 | f73b190 |
| disk-cleanup | tests/ (4 files incl. JS DOM) | 43/43 | a095909 |
| wifi-network-monitor | tests/test_monitor.py + run_tests.py | 11/11 | 3f62ed1 |
| video-tools | tests/test_app.py + run_tests.py | 15/15 | (new private repo, master) |
| project-hub | tests/test_hub.py + run_tests.py; /api/storage + Storage UI table | 13/13 | ce1ae21 |
| singing-practice-tools | run_tests.py wraps existing gate | 70 checks, 1 red | 57ad809 |
| money-plan | tests/ (3 files) + run_tests.py | 28/28 | pushed to new private repo |

Final orchestrator run: 10/11 green at 2026-10-09 03:28 (`--include-money-plan`).

## Where it stopped

All Phase 1 projects done. NEXT: build C:\Projects\run_all_tests.py, then
money-plan (re-check `find money-plan -type f -mmin -60` - quiet since the
02:30 commit as of ~03:20), then Phase 3.

KNOWN-RED (not ours): singing-practice-tools suite_test_musicxml_import ->
test_las_mananitas_chapter_preserves_both_arrangements expects chapter name
'Two Arrangements'; chapter_las_mananitas/import_manifest.json is mid-rewrite
by the in-flight control-layout/pitch-view tasks. Re-verify after they land.

CAUTION (note for next agent): the singing-practice-tools commit 57ad809
accidentally included 4 already-staged chapter_pdmx_* file deletions - `git
status` had them as `D ` (staged) before commit ran. They were deleted on
disk already; recoverable from history if the other agent didn't want them.
