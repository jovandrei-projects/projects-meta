# Working notes for agents: C:\Projects

Read this first, then the `AGENTS.md` inside the project you are working on.

## What this folder is

`C:\Projects` is a flat container of unrelated local projects. Each subfolder is
its own project and its own git repository. There is no root repository, no
shared package manifest and no build that spans them. Nothing here imports
anything from a sibling - if two projects need the same code, that is a
conversation to have, not something to quietly wire up.

## Which file owns what

The same fact in two files becomes two facts that disagree. So:

| File | Owns |
|---|---|
| `C:\Projects\AGENTS.md` (this file) | The project index, machine-wide facts, traps that bite in every project, the port registry, the task-workspace convention |
| `<project>\AGENTS.md` | That project's purpose, layout, traps, verification commands |
| `<project>\ROADMAP.md` | That project's phase list and status |
| `<project>\.agent_tasks\QUEUE.md` | Which of that project's tasks is next |
| `<project>\.agent_tasks\<task>\STATE.md` | The steps of work in flight on one task |

**Do not restate a project's specifics here, and do not restate machine facts in
a project file.** When adding a project, follow *Starting a new project* below
and add a row to the index; that is the whole ritual.

## The projects

| Project | What it is | Entry point |
|---|---|---|
| `wifi-network-monitor` | Home-network diagnostics and a live dashboard. Holds private device identifiers, MACs and router data. | `app/wifi-live-monitor.bat` |
| `chrome-bookmarks` | Reads, categorizes and rewrites Chrome bookmarks; flags dead links. | `python organize.py report` |
| `disk-cleanup` | Read-only inventory of `C:` plus a viewer, to decide what to delete. Never cleans automatically. | `python scan.py`, `python app.py` |
| `nirvana-concert-images` | Resumable scraper archiving every concert image from livenirvana.com into `data/images/` + flat `data/all/`. | `python scrape.py` |
| `singing-practice-tools` | Solfege exercise transcription and a voice-analysis practice site. | `VocalCoach/backend/web_app.py` |
| `model-compare` | Cost-vs-performance comparison of the Copilot and Devin model pickers; `generate_report.py` emits a static interactive chart + report. | `python generate_report.py`, open `index.html` |
| `project-hub` | Index page + launcher for the local services: live status, start/stop/restart, links. | `python hub.py` or `start-hub.bat`, then `http://127.0.0.1:8760` |

Two of these hold data that must not leave the machine: `wifi-network-monitor`
(device inventory, MACs, router responses) and `chrome-bookmarks` (the bookmark
set is a personal browsing record, and `data/` contains verbatim copies of it).
Treat `data/` as private and gitignored in every project unless its own
`AGENTS.md` says otherwise.

All of them carry the `.agent_tasks` workspace described below; follow its
convention in any of them.

## This machine

Windows 11. Python 3.11 at `C:\Python311\python.exe`, on `PATH` as `python`.
Node 18.17.1. `gh` is installed and authenticated as `jovandrei`.

**Two shells are available and they are not interchangeable.** PowerShell is
the default Windows shell; Git Bash is installed at `C:\Program Files\Git`.
Whichever you use, use it deliberately:

- PowerShell: `&&` does not chain commands - use `;`.
- Git Bash: chains with `&&`, but **mangles arguments that look like Unix
  paths**. `tasklist /FI "IMAGENAME eq chrome.exe"` fails there because `/FI`
  is rewritten to `C:/Program Files/Git/FI`. Prefix with `MSYS_NO_PATHCONV=1`,
  or run such commands from PowerShell, or invoke them from Python with a
  `subprocess` argument list, which bypasses the shell entirely.
- Git Bash also does not know `/tmp` when the program is *Windows* Python.
  `python -c "open('/tmp/x','w')"` raises `FileNotFoundError`. Use
  `%LOCALAPPDATA%\Temp` or the project's own `data/`.

Stdlib-only is the default for Python here. `singing-practice-tools` is the one
project with real dependencies (`requirements.txt`), and numpy on this machine
must not be upgraded - see that project's notes. Do not add a dependency to the
others without asking.

## Traps that apply everywhere

1. **The console is cp1252.** Any script that prints data it did not author -
   file paths, bookmark titles, song names - will eventually hit
   `UnicodeEncodeError` on an accented character, a Japanese interpunct or a
   non-breaking hyphen, and die mid-run. Two projects have been bitten.
   Write real output to a UTF-8 file and make console printing fall back to
   `backslashreplace`. Never "fix" it by stripping characters from the data;
   the data is correct and the terminal is not.
2. **OneDrive is in the path of some work.** `singing-practice-tools` has a
   copy under `C:\Users\andry\OneDrive\...`, where files lock briefly during
   sync, and `disk-cleanup` must never open a cloud placeholder file. If a
   write fails with a sharing violation, suspect sync before suspecting code.
3. **Verify against reality before building on an assumption.** The pattern
   that keeps paying off in these projects: reproduce a known-good value first,
   then trust the code that produced it. `chrome-bookmarks` derived Chrome's
   checksum algorithm by reproducing the live file's existing digest before
   writing anything; `disk-cleanup` disproved a documented claim about
   last-access times by measuring it. Assertions in these files are meant to
   stay checkable - re-derive rather than inherit.
4. **Local servers bind loopback only.** Every viewer here exposes the contents
   of this machine. `wifi-network-monitor` has a deliberate, token-protected
   opt-in for phone access; that is the exception and it was designed as one.
   Do not add a `0.0.0.0` bind for convenience.

## Port registry

Local servers, so a new one does not collide:

| Port | Project |
|---|---|
| 8731 | `singing-practice-tools` practice site |
| 8760 | `project-hub` index page |
| 8765 | `wifi-network-monitor` dashboard |
| 8770 | `disk-cleanup` viewer |
| 8780 | `model-compare` static preview (optional; file also opens directly) |

Pick the next free port in the 87xx range for anything new and add it here.

## Working habits

These are the user's stated preferences, learned across sessions, and they hold
in every project in this folder.

- **Say what is not working.** "This fails and here is why" beats an optimistic
  summary. Correct the user when they are wrong.
- **Do the testing yourself.** Do not hand over a command to run and report
  back, unless it genuinely needs the user's voice, hardware or credentials.
- **Explain reasoning, not just conclusions**, proportionately: "I tested X,
  got Y, concluded Z, changed W, now it gives V."
- **Destructive work is opt-in and reversible.** Two of these projects exist to
  delete things - files, bookmarks - and both separate scanning from deleting,
  back up first, and leave the decision to the user. Keep that shape.
- **Commit in groups a reviewer can follow**, messages saying why not what.
  Never push without being asked.
- **Do not dump generated files into a project root.** Use `data/` or a
  subfolder.
- **Assume the session could end at any moment.** Write findings down as you
  get them; a number that only exists in the chat transcript is lost. The
  task workspace below is the mechanism that makes this survivable.

## The task workspace - how sessions resume here

Every project carries a `.agent_tasks/` folder so that "Continue from
`.agent_tasks/QUEUE.md`." is a complete first prompt. The full contract lives
in each project's `.agent_tasks/README.md`; the convention is the same in all
of them:

- **`QUEUE.md`** - every task, one line each, in intended order. Answers
  "what next".
- **`<task>/STATE.md`** - objective, phased checklist, and a *Where it
  stopped* line that says concretely what to do first. Answers "where in it".
  Kept to about one screen; a step is one line and verifiable.
- **`<task>/scratch/`** - gitignored dumping ground for long output. A
  finding that only exists there is lost; lift conclusions into `STATE.md`,
  or into `ROADMAP.md` if it is a measurement.
- **`efficiency_stats.md`** - one row of token cost per session, appended
  before stopping.
- **`ROADMAP.md`** - the project's phases, each step a `- [ ]` ticked `[x]`
  only when done *and verified*. Product state lives here, task state lives
  in `STATE.md`; a step that lands a roadmap item ticks both in one commit.

Resuming a session: read the project's `AGENTS.md`, then `QUEUE.md`, then the
`STATE.md` of any task that is not `done`. If the queue is empty, the
roadmap's unchecked items are the default source of the next task. Run
`git status` before changing anything - work may be intentionally uncommitted
while the user evaluates it. Do not open a second task while one is
`in progress` unless the user asks.

## Starting a new project

1. `git init`; `.gitignore` covers `data/`, `__pycache__/` and
   `.agent_tasks/*/scratch/` at minimum.
2. Copy `_templates/new_project/` into the project root - it carries the
   `.agent_tasks` skeleton (contract, queue, `STATE.md` template, stats
   file), a stub `AGENTS.md` and a stub `ROADMAP.md`.
3. Fill in the project's `AGENTS.md`: purpose, ground rules, entry points,
   verification commands. Traps get appended as they are hit.
4. Fill in `ROADMAP.md`: phases in order, each step a `- [ ]` that can be
   checked rather than judged, plus a decisions table if choices were settled
   up front.
5. File the first task in `QUEUE.md` - with a `<task>/STATE.md` folder if it
   will outlive one session, under *Not yet filed* if not.
6. Add a row to the project index above, and a port to the registry if the
   project serves anything.
