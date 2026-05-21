# mini-moulinette Python Migration

## Current behavior findings

- Entry script hardcodes `~/mini-moulinette` and fails when installed elsewhere.
- `run_norminette` is called before declaration in `mini-moul.sh`, so each run prints `command not found`.
- Scoring intentionally gates later marks after the first failed exercise (`break_score` behavior).
- Test execution is compile-then-run of standalone C harnesses. Most harnesses return `0` on success and non-zero on failure.
- Some harnesses use relative runtime paths (for example C06 tests with `cp ../ex01/...`), so working directory handling matters.

## Recommended C test strategy

Use Python as the orchestrator and keep C tests as separate executables.

Why this is the best path now:

- Lowest migration risk: existing C tests are already written and mostly working.
- Fastest delivery: no mass rewrite of test cases into another protocol.
- Easy debugging: each test remains a normal C source file that can be compiled/run manually.
- Compatible with strict norm constraints on student code.

## Alternative strategies considered

1. Add a JSON protocol between C tests and Python:
- Pros: structured results, easier machine reporting.
- Cons: high rewrite cost across all tests, introduces protocol maintenance burden.

2. Add a C/C++ abstraction layer and shared test framework:
- Pros: better long-term consistency.
- Cons: substantial engineering effort for little short-term value.

## Python conversion outline

- CLI: Typer (`mini_moul_app/cli.py`, exposed as `mini-moul`).
- Pathing: resolve repo paths from `__file__`, no hardcoded home path.
- Workspace: create a temporary workspace in `/tmp` by default, copy `mini-moul` contents and student sources there, run tests, then clean up.
- Execution:
  - Validate assignment name (`C00..C13`) and enforce matching target directory name.
  - Optional `norminette` run.
  - For each exercise (parallelizable via `--jobs`):
    - compile a sanity build with `-Wall -Werror -Wextra`,
    - compile each test harness,
    - run test binaries and collect exit codes,
    - preserve score gating behavior.
- Output: rich progress bars + consolidated end-of-run error report.

## What this migration does not change yet

- C test case content and assertions.
- Coverage limitations in existing harnesses.
- Accuracy relative to official moulinette.

## Session Handoff (2026-05-19)

### Summary of changes made

- Added a full Python/Typer runner and later split it into the `mini_moul_app` package.
- Switched terminal formatting from manual ANSI escapes to `rich`.
- Replaced the large ASCII banner with a compact header: `mini v2 by Mikadore`.
- Added parallel execution for exercises with live progress rows (`--jobs`).
- Added consolidated error reporting at the end of execution.
- Moved workspace strategy to a temporary directory (`/tmp` by default), while preserving compatibility with existing `../../../../exNN/...` include paths.
- Kept `norminette` execution focused on each target exercise directory, not the temporary copied test harnesses.
- Split the Python runner into a package (`mini_moul_app`) and reduced `mini_moul.py` to a thin compatibility entrypoint.
- Added missing-exercise detection before compile/run, reporting skipped exercises as `MISSING` instead of surfacing compiler include errors.
- Integrated per-exercise norminette checks into the execution pipeline without blocking compile/run, and report those notices in the summary.
- Removed obsolete shell orchestration files: `mini-moul/test.sh` and `mini-moul/config.sh`.

### File replacement mapping

- Old runtime entrypoint (shell): `mini-moul.sh`
  - Status: compatibility shim.
  - Current role: bootstraps an editable `uv` tool install from the local checkout, then forwards to the Python CLI.
  - Replacement for new work: `mini_moul_app/cli.py` via the installed `mini-moul` command.
- Old test orchestration logic (shell): `mini-moul/test.sh`
  - Status: legacy reference behavior.
  - Replacement for new work: orchestration inside `mini_moul_app/execution.py`.
- Color constants / shell formatting (`mini-moul/config.sh` + inline ANSI usage)
  - Replacement: `rich` output in `mini_moul_app/reporting.py`.

### New/updated project files

- New: `mini_moul.py` (thin compatibility entrypoint).
- New: `mini_moul_app/` (package with CLI, execution, reporting, discovery, and workspace modules).
- New: `pyproject.toml` (dependencies, script entrypoint, build config).
- Updated: `README.md` (v2 usage notes and behavior).
- Updated: `MIGRATION_TO_PYTHON.md` (this file).

### Next-session continuation pointers

- Primary file to continue implementation: `mini_moul_app/cli.py`.
- Core behavior now lives in:
  - `mini_moul_app/discovery.py`
  - `mini_moul_app/execution.py`
  - `mini_moul_app/reporting.py`
  - `mini_moul_app/workspace.py`
- Run locally from repo root:
  - `uv run mini-moul --target /path/to/42piscine/C01`
- Compatibility entrypoint from repo root:
  - `python3 mini_moul.py --target /path/to/42piscine/C01`
- Run from inside an assignment dir:
  - `uv run --with-editable /path/to/mini-moulinette mini-moul`
- For debugging temp artifacts:
  - add `--keep-workspace`
  - override temp root with `--workspace-root /some/path`

### Current local validation

- The old `exerc` symlink is no longer part of the local setup.
- Current local reference tree is `42piscine/`, validated through `C07`.
- Observed results with `./.venv/bin/python mini_moul.py --target /home/mikadore/mini-moulinette/42piscine/CXX --no-color`:
  - `C00`: `88/100` (`ex05` norminette notice, `ex08` missing)
  - `C01`: `100/100`
  - `C02`: `84/100` (`ex11` compile failure, `ex12` compile failure and norminette issues)
  - `C03`: `100/100`
  - `C04`: `100/100`
  - `C05`: `88/100` (`ex08` missing)
  - `C06`: `100/100`
  - `C07`: `66/100` (`ex04` compile failure)
