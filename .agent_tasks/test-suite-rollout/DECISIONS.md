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

## Follow-up fixes (2026-10-09, after the suites were exercised)

- **money-plan CSRF on `/api/catmap` (fixed, commit 86cd1ad).** `do_POST`
  accepted mutating requests with no custom header, so a cross-origin page
  could write category mappings. Server now requires `X-Money-Plan-Request`
  on POSTs and `apiFetch` sends it - the same guard project-hub and
  video-tools already had. Regression test asserts 4xx rejection without it.
- **thermalwatch web-sibling path escape (fixed, commit b164ced).**
  `send_file` used a `startswith(WEB)` prefix check, which accepts paths in
  a sibling like `web-sibling/`. Replaced with resolved-path containment;
  test covers real-file accept, sibling reject, traversal reject.
- **singing-practice-tools las_mananitas test (updated, commit 3228f93).**
  Not a bug: the other agent's rewrite settled on 7 harmonica/guitar
  exercises ("Las Mañanitas — Harmonica/guitar"). Test updated to the new
  contract. The manifest `body_sha256` drift was purely `|` -> `||`
  barlines (byte-identical otherwise, verified by canonicalizing), so the
  test canonicalizes barline runs before hashing - real note/lyric drift
  still fails. tempo-beat-unit's STATE.md had already documented this
  drift as a known pre-existing failure at HEAD.

## Context a new agent might miss

- **Branch names differ across repos.** `main` for most, but `money-plan`
  and `video-tools` are on `master`. Check `git branch --show-current`
  before scripting pushes.
- **The las_mananitas `.mxl` source is not in the repo.** The manifest's
  `body_sha256` is a provenance record; the import cannot be replayed
  locally to regenerate it. If the `|`/`||` drift should be fixed at the
  source rather than canonicalized in the test, the original
  `las-mananitas-do-para-armonica-y-acompanada-de-guitarra.mxl` lives
  wherever the user keeps user-supplied scores.
- **singing-practice-tools still carries ~27 modified/untracked paths**
  from the other agent's in-flight tasks (control-layout, pitch-view,
  tempo-beat-unit). Leave them uncommitted; stage only your own files and
  check `git diff --cached` before committing - the index has surprised
  once already (see Incidents).
- **The money-plan quiet-guard in `run_all_tests.py` is now vestigial.**
  The other agent's work finished 2026-10-09 ~02:30; the guard just means
  money-plan reports `skipped` in the summary whenever its files are
  <60 min old. Use `--include-money-plan` or run `run_tests.py` there
  directly - a `skipped` line is not a failure.
- **`C:\Users\andry\AppData\Local\Temp\lm.json`** is a leftover scratch
  file from lyric-list inspection; safe to delete, nothing depends on it.
- **`money-plan-ui/` appeared 2026-10-09 ~10:20** - a fork of money-plan
  that another agent created mid-session (has its own .agent_tasks, .git
  pointer file, same module files incl. the pre-fix stdout idiom). It is
  IN FLIGHT: do not edit it, do not index it yet, and do not assume its
  test suite exists. When its work settles it needs the same treatment:
  `tests/` + `run_tests.py`, the `reconfigure` stdout fix, and a row in
  the root AGENTS.md index + root .gitignore + port registry (it will want
  a port other than 8800 if both apps can run at once).

## Open decisions and tasks for the user

Tick `[x]` and note the outcome on the item when decided/done - the note
is the record the next agent works from. Roughly ordered by importance.

- [x] **Browser automation layer?** Current coverage is HTTP smoke tests
      plus disk-cleanup's Node-DOM pattern; real clicking needs selenium +
      a driver (new pip deps, and the machine default is stdlib-only).
      Options: (a) stay with smoke + Node-DOM, (b) install selenium and
      name which projects get it.
      Answer: (2026-10-09) User approved installing a browser layer;
      **Playwright** was chosen over Selenium because it was already fully
      installed on the machine (pip package + Chromium binaries in
      %LOCALAPPDATA%\ms-playwright) - zero new browser deps. All 9 serving
      projects got `tests/test_browser.py` (unittest-style, `--quick`-gated,
      skips without the package/binaries). Each spawns the app on an
      alternate port (or in-process for money-plan's fixture store),
      asserts the page boots, exercises one read-only control, and fails on
      uncaught JS errors. model-compare loads via file:// (real usage).
- [ ] **Keep `money-plan` on GitHub?** The repo was created `--private`
      and nothing under `data/` was pushed. If it should not be on GitHub
      at all, delete the remote repo.
      Answer:
- [ ] **Pre-push hooks?** `run_all_tests.py` is not wired into git hooks -
      hooks are per-clone and a missing optional dep (video-tools venv)
      could block legitimate pushes. Options: (a) leave manual, (b) add a
      `pre-push.sample` each repo can opt into, (c) wire real hooks.
      Answer:
- [ ] **Log cap OK?** Policy is RotatingFileHandler 1 MB x 5 (~6 MB per
      app, ~60 MB worst case across everything), surfaced in project-hub's
      Storage panel. Edit `TESTING.md` if you want different limits.
      Answer:
- [x] **unittest vs pytest?** Suites are stdlib `unittest` per the
      stdlib-only rule. If pytest is ever wanted, that is a dependency
      decision for you; the `tests/` layout ports over unchanged.
      Answer: (2026-10-09) pytest 9.1.1 installed as an OPTIONAL runner -
      it collects all 265 unittest tests unchanged; suites stay
      unittest-style so `run_tests.py` keeps working with zero deps.
      Installing it caught a real latent bug: money-plan's
      `analyze.py`/`store.py`/`fetch.py` replaced `sys.stdout` with a new
      `TextIOWrapper` around `sys.stdout.buffer`, which closes pytest's
      capture stream on GC (and would crash under `pythonw`, where stdout
      is None). Switched to guarded `sys.stdout.reconfigure()` - same
      idiom run_tests.py already used.
- [ ] **Confirm the 4 `chapter_pdmx_*` deletions in 57ad809.** They were
      already-staged deletions from the other agent's work that my commit
      swept in (see Incidents). If they were not intended, restore from
      `57ad809^`. Verify intent, then tick.
      Answer:
- [ ] **Remove the money-plan quiet-guard?** `run_all_tests.py` still
      skips money-plan when files there are <60 min old; the other agent's
      work is finished, so the guard is vestigial. Keep (harmless, skips
      are visible as `skipped` not `ok`) or strip it to always run.
      Answer:
- [ ] **Fix the las_mananitas `|`/`||` drift at the source?** The test
      canonicalizes barline runs before hashing, so the suite is green and
      real drift still fails. To make the manifest literally match instead,
      re-import needs the original `.mxl` (not in the repo - see Context).
      Options: (a) accept canonicalization, (b) re-import from the mxl,
      (c) rehash the manifest to the current txt.
      Answer:
- [ ] **Standardize branch names?** `money-plan` and `video-tools` are on
      `master`; everything else is on `main`. Cosmetic - rename only if it
      bothers you.
      Answer:
- [ ] **Delete `%LOCALAPPDATA%\Temp\lm.json`.** Scratch file from lyric
      inspection in this session; nothing depends on it.
