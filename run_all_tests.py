"""Run every project's test suite and report one summary.

    python run_all_tests.py              all projects, full mode
    python run_all_tests.py --quick      pass --quick to runners that accept it
    python run_all_tests.py --only hub,thermalwatch   subset by name fragment

Per-project output lands in logs/test-run-<ts>-<project>.log next to this
file; the console gets a compact summary. Exit code is nonzero if any suite
fails.

A project runs via its own run_tests.py when present, else via
`python -m unittest discover -s tests` when it has a tests/ dir.
"""
import datetime
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
PER_PROJECT_TIMEOUT = 1800

try:
    sys.stdout.reconfigure(errors="backslashreplace")
except Exception:
    pass


def projects():
    out = []
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name == "_templates":
            continue
        if (d / "run_tests.py").is_file():
            out.append((d.name, [sys.executable, "run_tests.py"]))
        elif (d / "tests").is_dir():
            out.append((d.name, [sys.executable, "-m", "unittest",
                                 "discover", "-s", "tests", "-v"]))
    return out


def main():
    quick = "--quick" in sys.argv
    only = None
    for i, a in enumerate(sys.argv):
        if a == "--only" and i + 1 < len(sys.argv):
            only = [x.strip() for x in sys.argv[i + 1].split(",")]

    LOG_DIR.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    results = []
    for name, cmd in projects():
        if only and not any(x in name for x in only):
            continue
        run_cmd = cmd + (["--quick"] if quick and "run_tests.py" in cmd else [])
        log_path = LOG_DIR / ("test-run-%s-%s.log" % (stamp, name))
        t0 = time.time()
        print("[run ] %s ..." % name, flush=True)
        try:
            proc = subprocess.run(run_cmd, cwd=str(ROOT / name),
                                  capture_output=True, encoding="utf-8",
                                  timeout=PER_PROJECT_TIMEOUT,
                                  errors="backslashreplace")
            out = (proc.stdout or "") + (proc.stderr or "")
            status = "ok" if proc.returncode == 0 else "FAIL"
            note = "exit %d" % proc.returncode
        except subprocess.TimeoutExpired:
            out = "timed out after %ds" % PER_PROJECT_TIMEOUT
            status, note = "FAIL", "timeout"
        except OSError as exc:
            out = str(exc)
            status, note = "FAIL", "spawn error"
        dur = time.time() - t0
        log_path.write_text(out, encoding="utf-8", errors="replace")
        results.append((name, status, dur, note))
        print("[%s] %s  (%.1fs, %s)  log: %s"
              % (" ok " if status == "ok" else status, name, dur, note,
                 log_path.name), flush=True)

    width = max((len(n) for n, *_ in results), default=8)
    print("\n=== summary %s ===" % stamp)
    for name, status, dur, note in results:
        print("  %-*s  %-7s %7.1fs  %s" % (width, name, status, dur, note))
    failed = [n for n, s, *_ in results if s == "FAIL"]
    if failed:
        print("FAILED: " + ", ".join(failed))
        return 1
    print("all green" if results else "nothing ran")
    return 0


if __name__ == "__main__":
    sys.exit(main())
