# projects-meta

Workspace notes, shared testing policy, and cross-project orchestration
for the `C:\Projects` folder.

- `AGENTS.md` - the project index, machine facts, traps, port registry,
  and the `.agent_tasks` task-workspace convention
- `TESTING.md` - the shared testing/logging policy
- `run_all_tests.py` - runs every project's suite and prints one summary
- `requirements-dev.txt` - shared dev/test tooling (pytest, Playwright)

Each subfolder is its own project and its own git repository. There is
no shared build and nothing imports across siblings.
