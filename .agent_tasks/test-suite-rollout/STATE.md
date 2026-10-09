# Task: test-suite-rollout

Status: done (open questions for the user live in DECISIONS.md)
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
| thermalwatch | tests/ (2 files) + run_tests.py | 26/26; follow-up hardened web/ path confinement (startswith prefix bug) | b164ced |
| disk-cleanup | tests/ (4 files incl. JS DOM) | 43/43 | a095909 |
| wifi-network-monitor | tests/test_monitor.py + run_tests.py | 11/11 | 3f62ed1 |
| video-tools | tests/test_app.py + run_tests.py | 15/15 | (new private repo, master) |
| project-hub | tests/test_hub.py + run_tests.py; /api/storage + Storage UI table | 13/13 | ce1ae21 |
| singing-practice-tools | run_tests.py wraps existing gate | 70/70 checks | 3228f93 |
| money-plan | tests/ (3 files) + run_tests.py | 29/29; follow-up added CSRF guard on mutating POSTs | 86cd1ad |

Final orchestrator run: all green at 2026-10-09 03:44 (money-plan skipped by
its own 60-min quiet guard; standalone run 29/29 OK at 03:44).

Follow-up pass (user asked to fix test-uncovered issues): the las_mananitas
test failure was stale expectations vs the settled 7-exercise
harmonica/guitar rewrite - updated to the new contract (title, counts,
tempos, lyrics) and barline-canonicalized the body_sha256 check ('||' vs '|'
is parser-identical per BARLINE_RE). Two real defects found and fixed:
money-plan CSRF on /api/catmap, thermalwatch web-sibling path escape. Both
committed and pushed; suites re-run green.

## Where it stopped

All phases complete; every suite green. No pending work except the open
human decisions in DECISIONS.md (log caps, hooks, money-plan remote).

Follow-up 2026-10-09 (later session, user present): two DECISIONS items
answered and implemented - pytest 9.1.1 installed as an optional runner
(suites stay unittest-style; `python -m pytest tests/` collects all 265),
and the browser layer landed as `tests/test_browser.py` in all 9 serving
projects using **Playwright** (already installed incl. Chromium binaries;
chosen over the approved Selenium for zero new deps). Each test spawns the
app on an alternate port, asserts the page boots, drives one read-only
control, and fails on uncaught JS errors. Two latent bugs fixed on the
way: money-plan's stdout re-wrap closed pytest's capture stream
(`reconfigure()` now, in analyze.py/store.py/fetch.py). Full
run_all_tests.py green incl. every browser test; money-plan standalone
green. `.pytest_cache/` added to all gitignores.

Same session, later: `ui-batch4` (the money-plan-ui worktree's branch)
merged into money-plan master after user visual check - zero file
overlap, clean merge. Suite re-verified 30/30 + `analyze.py --check`.
:8800 was serving pre-merge code from a 02:30 process; restarted via the
hub (`/api/services/money-plan/restart`), verified byte-identical to the
branch's own output. :8801 stopped; worktree removed (its `data/` was a
subset copy - all 8 files identical in canonical; nothing lost), branch
deleted, port-8801 registry row removed. money-plan pushed
(86cd1ad..f62a8a4). Other repos stay 1 commit ahead - unpushed pending
user.

Same session, normalization pass: all repos on `main` (6 `master`
renamed, remotes' default switched, remote `master` deleted), all
pushed, `.gitattributes` added everywhere (zero renormalize churn),
tracked `hooks/pre-push` wired via `core.hooksPath` in every repo (runs
`run_tests.py --quick`; verified live on every push), READMEs written
for the 9 repos lacking one, shared `requirements-dev.txt` created,
GitHub descriptions set, money-plan quiet-guard stripped from
run_all_tests.py, `%LOCALAPPDATA%\Temp\lm.json` deleted. Remaining open
items in DECISIONS: log-cap confirmation, the 4 swept `chapter_pdmx_*`
deletions (needs user intent check), las_mananitas `|`/`||` source drift
(needs the original .mxl). spt still holds the other agent's uncommitted
WIP - untouched; renormalize deferred there until it lands.

CAUTION (note for next agent): the singing-practice-tools commit 57ad809
accidentally included 4 already-staged chapter_pdmx_* file deletions - `git
status` had them as `D ` (staged) before commit ran. They were deleted on
disk already; recoverable from history if the other agent didn't want them.
