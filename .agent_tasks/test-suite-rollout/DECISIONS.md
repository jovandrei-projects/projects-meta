# Decisions log - test-suite-rollout

The user was asleep for this run; anything that would normally be a question
is recorded here instead of blocking.

## Decisions made (rationale included)

1. **Test framework: stdlib `unittest`, not pytest.**
   The machine rule is stdlib-only and new dependencies need asking. unittest
   gives discovery (`python -m unittest`), fixtures, skips and subTests with
   zero installs. If pytest is ever wanted, the `tests/` layout ports over.

2. **One test mindset, per-project code.**
   Every project gets the same *shape*: `tests/` dir, `run_tests.py` wrapper,
   `logs/` for output. Code is copied per project, never imported across
   projects - the root AGENTS.md forbids sibling imports. The shared
   convention lives in `C:\Projects\TESTING.md`.

3. **Logging: stdlib `logging` + `RotatingFileHandler`, `logs/` per project.**
   Default policy: one `logs/<app>.log`, UTF-8, 1 MB per file, 5 backups
   (~6 MB cap per app), `logs/` gitignored. Console handlers keep the
   cp1252 `backslashreplace` fallback. Scripts that already log to `data/`
   (nirvana scrape.log, chrome-bookmarks report files) keep doing so -
   rotation is added where a file can grow unbounded on repeat runs.
   Policy document: `C:\Projects\TESTING.md` (tracked in projects-meta).

4. **Log deletion policy: rotation, not sweeps.**
   Bounded retention is built into RotatingFileHandler (size cap) rather
   than a cron-style deleter - no process has to remember to run. The
   project-hub panel surfaces sizes so a log growing toward its cap is
   visible before it matters. Estimated worst case across all projects:
   ~60 MB of logs total. A disk-space gauge in the hub covers "running out
   of space without warning" more honestly than log deletion alone.

5. **"Selenium" layer = HTTP smoke tests + the Node-DOM pattern, not real
   Selenium.** Selenium needs pip packages and a browser driver - that is a
   dependency decision for the user. What was built instead: every web app
   gets a smoke test that spawns it on an alternate port and asserts real
   HTTP responses (status, JSON shape, key markers in HTML). disk-cleanup
   already has `test_render.js` (Node VM + stubbed DOM against a live
   server) - that test is wired into its suite, and it is the template if
   real browser testing is ever wanted.

   OPEN DECISION for the user: install selenium + a driver if true browser
   automation is wanted. Everything needed to add it later is in place.

6. **Performance testing = time budgets inside smoke tests.**
   Each suite can mark a test `@slow`/perf with a generous wall-clock
   budget (e.g. endpoint < 2 s, report generation < 60 s). These catch
   order-of-magnitude regressions, not micro-benchmarks. A real perf
   harness is an open decision.

7. **Repo creation for the three without remotes: all `--private`.**
   senior-safety-mx and video-tools have local repos but no remote;
   money-plan has neither remote nor (at start) was it in projects-meta's
   index of pushed repos. All three were created PRIVATE - the org default
   for the existing repos is private (singing-practice-tools is documented
   private) and all three touch personal data themes. Even so: before
   pushing money-plan, every tracked file was scanned for account numbers /
   transaction content, and `data/` stays gitignored.

8. **singing-practice-tools: tests committed, pre-existing edits not.**
   ~31 modified files were in the working tree at session start (last
   touched 2026-10-07). Convention says uncommitted work may be intentional
   - the rollout only stages files it created itself.

9. **projects-meta gets the rollout docs.**
   STATE.md/DECISIONS.md live at `C:\Projects\.agent_tasks\test-suite-rollout\`
   and are tracked by projects-meta so resumability survives a clone.
   `.agent_tasks/*/scratch/` is gitignored there as elsewhere.

10. **project-hub monitoring = `/api/storage`, not a per-app logger rollout.**
    The per-app `RotatingFileHandler` idea in the original design was dropped
    in favor of what already exists: each dashboard already writes bounded
    logs (`logs/` per project, sqlite retention tiers in the monitors). The
    hub's new `storage_report()` + Storage table gives the "watch for a
    runaway log / disk filling" layer the user asked for without rewriting
    eleven logging stacks. `/api/storage` reports sizes only, never content.

11. **money-plan waited ~70 min of quiet, not a clock-time rule.**
    Its last change was the other agent's own 02:30 commit; work started at
    ~03:40 once `find -mmin -60` came back clean. Tests patch `store.DB` and
    the inbox paths onto temp dirs - zero real financial data in fixtures.

## Incidents

- **singing-practice-tools commit 57ad809 swept in 4 staged deletions.**
  `chapter_pdmx_danny_boy_c_major/` and `chapter_pdmx_na_simplified/` files
  were already staged `D` by the in-flight work; `git commit` took the whole
  index. Nothing was deleted by this rollout (they were gone on disk
  already) and the files are recoverable from git history if unwanted.
  Lesson for future runs here: check for staged changes too, not just ` M`.

## Open questions left for the user

- Real Selenium/browser-driver testing wanted? (needs pip install)
- money-plan GitHub repo: created `--private`. If it should not be on
  GitHub at all, delete the remote repo; nothing under `data/` was pushed.
- singing-practice-tools has one known-red test
  (`test_las_mananitas_chapter_preserves_both_arrangements`) pinned to the
  in-flight manifest rewrite - confirm with the other agent's task whether
  "Two Arrangements" vs "Harmonica/guitar" is the intended final name.
- Should `run_all_tests.py` also be wired as a git pre-push hook in each
  repo? Left undone - hooks are per-clone and a failing push-hook on a
  machine with optional deps (video-tools venv) could block legitimate
  pushes. A `pre-push.sample` or a note in TESTING.md may be enough.
