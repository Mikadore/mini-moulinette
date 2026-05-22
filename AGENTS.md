# AGENTS.md

## Purpose

`mini-moulinette` is a local helper for 42 Piscine C exercises. It runs repository-provided C test harnesses against student solutions and gives a moulinette-like score with practical diagnostics.

Current implementation is Python-first (Typer + Rich), with C tests kept as standalone source files.

## Repo Structure

- `mini_moul_app/`
- `mini_moul_app/cli.py`: Typer entrypoint, option parsing, top-level orchestration.
- `mini_moul_app/discovery.py`: assignment resolution, student-file reference extraction, missing/unexpected file checks.
- `mini_moul_app/execution.py`: per-exercise pipeline, compiler/norminette commands, parallel execution.
- `mini_moul_app/reporting.py`: Rich output, score summary, grouped reports.
- `mini_moul_app/workspace.py`: temporary workspace creation and exercise isolation.
- `mini_moul_app/models.py`: result dataclasses.
- `mini_moul.py`: thin compatibility entrypoint.
- `mini-moul/`: test harness tree (`tests/CXX/exYY/*.c`) and shared constants.
- `mini-moul.sh`: compatibility wrapper that installs/runs the Python CLI.
- `42piscine/`: local student solutions used for validation in this repo.
- `ISSUES.md`: triaged upstream backlog and PR analysis baseline.
- `MIGRATION_TO_PYTHON.md`: migration history and implementation notes.

## Execution Model

For each exercise:

1. Resolve expected student files from harness includes (`../../../../exYY/...`).
2. Warn on superfluous files in the exercise directory.
3. Mark `MISSING` and skip compile/run when required student files are absent.
4. Run `norminette` in the exercise directory (non-blocking for compile/run).
5. Prepare isolated temp workspace under `/tmp` by default.
6. Compile a sanity build with strict flags.
7. If a compile fails only due to `-Werror`, retry compile without `-Werror`, keep it non-fatal, and record warnings.
8. Compile harness binary and run it with timeout.
9. Aggregate results and compute score with legacy gate behavior.

## Result and Scoring Semantics

- `OK` (green): compile and tests passed without norminette/compiler warning notices.
- Orange scored mark (`passed/checks`): tests passed, but norminette notices and/or warning-only `-Werror` compile failures were detected.
- `MISSING`: required exercise files not found; compile/run skipped.
- `KO`: compile or test run failed.
- Extra files are reported at the end in `Extra file report` and do not change score/result labels.

Score behavior intentionally matches legacy mini-moulinette style:
- One point per exercise until first `MISSING` or `KO`.
- After first blocking failure, later exercises do not increase score.
- Orange scored marks still count as passed exercises for score gating.

## Compiler and Norminette Rules

- Compiler command defaults to `cc`, overridable with `--compiler`.
- Compile flags default to `-Wall -Werror -Wextra`.
- Compile flags can be overridden with `CFLAGS` env var.
- If a compile fails only because of `-Werror`, the runner retries without `-Werror`, keeps the exercise orange, and reports warnings at the end.
- Norminette is optional (`--norminette/--no-norminette`).
- Special case: `C08/ex01` and `C08/ex02` use `norminette -R CheckDefine`.

## Local Validation Against Solutions

Single assignment:

```bash
./.venv/bin/python mini_moul.py --target /home/mikadore/mini-moulinette/42piscine/C01 --no-color
```

Batch run (`C00..C07`):

```bash
for d in C00 C01 C02 C03 C04 C05 C06 C07; do
  echo "== $d =="
  ./.venv/bin/python mini_moul.py --target "/home/mikadore/mini-moulinette/42piscine/$d" --no-color
  echo
done
```

Known baseline from current local tree:

- `C00`: `88/100`
- `C01`: `100/100`
- `C02`: `92/100`
- `C03`: `100/100`
- `C04`: `100/100`
- `C05`: `88/100`
- `C06`: `100/100`
- `C07`: `100/100`

Interpret score changes carefully:
- A score drop can be real regression.
- A score increase can be test fix or coverage change.
- Check `Result`, `Error report`, `Norminette report`, `Compiler warning report`, and `Extra file report` before concluding.

## Workflow for Test or Runner Changes

1. Edit the relevant module or harness file.
2. Run Python syntax check:
```bash
python3 -m py_compile mini_moul.py mini_moul_app/*.py
```
3. Run focused assignment test(s) under `42piscine/`.
4. Run `C00..C07` regression loop.
5. If behavior changed intentionally, update:
- `README.md` for user-facing behavior
- `MIGRATION_TO_PYTHON.md` for implementation history
- `ISSUES.md` if issue coverage status changed

## Common Pitfalls

- Do not assume harness output format is perfect; several tests are still coverage-limited.
- Some upstream PRs are duplicates or incomplete; use `ISSUES.md` before cherry-picking ideas.
- Keep student code and harness code separated; compile harnesses, do not embed runner logic in student files.
- Preserve deterministic tests; avoid timing-sensitive or locale-sensitive expectations unless explicitly handled.

## Priority Backlog Source

Use `ISSUES.md` as the primary backlog map. It already classifies upstream issues/PRs into:
- actionable items
- historical/resolved items
- noise/duplicates to ignore
