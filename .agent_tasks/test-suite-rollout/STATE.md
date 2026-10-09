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
- [ ] Root .gitignore: add missing project dirs, /nul, /logs/
- [ ] Delete junk `nul` file
- [ ] Commit projects-meta (AGENTS.md was already modified by earlier work -
      review it, it indexes money-plan/senior-safety-mx/favicon rule)

Phase 1 - per-project suites (order = least risky first)
- [ ] chrome-bookmarks
- [ ] model-compare
- [ ] nirvana-concert-images
- [ ] senior-safety-mx  (needs `gh repo create` - no remote yet)
- [ ] thermalwatch
- [ ] disk-cleanup  (already has test_render.js - wrap it)
- [ ] wifi-network-monitor
- [ ] video-tools  (needs `gh repo create`)
- [ ] project-hub  (tests + the Logs & Disk monitoring feature)
- [ ] singing-practice-tools  (tests only; do NOT commit existing edits)

Phase 2 - the guarded one
- [ ] money-plan: re-check mtimes; >= 60 min idle required. Then tests +
      `gh repo create --private` + push. Verify `data/` is gitignored and no
      private values are in tracked files BEFORE creating the repo.

Phase 3 - wrap-up
- [ ] run_all_tests.py green across every project that has tests
- [ ] Update root AGENTS.md: testing/logging policy pointer + TESTING.md
- [ ] Push every repo incl. projects-meta
- [ ] Final STATE.md update + per-project efficiency_stats.md rows

## Per-project notes (fill in as phases land)

| Project | Suite | Result | Commit |
|---|---|---|---|
| chrome-bookmarks | | | |
| model-compare | | | |
| nirvana-concert-images | | | |
| senior-safety-mx | | | |
| thermalwatch | | | |
| disk-cleanup | | | |
| wifi-network-monitor | | | |
| video-tools | | | |
| project-hub | | | |
| singing-practice-tools | | | |
| money-plan | | | |

## Where it stopped

START HERE on resume: read DECISIONS.md, then look at the checklist above for
the first unticked item. Each finished project is already committed+pushed, so
work never needs redoing. If money-plan still shows files modified within the
last hour (`find money-plan -mmin -60`), defer it again.
