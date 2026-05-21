from __future__ import annotations

import os
import signal
import subprocess
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from mini_moul_app.discovery import (
    available_assignments,
    missing_student_paths,
    unexpected_student_paths,
)
from mini_moul_app.models import CommandResult, ExerciseResult
from mini_moul_app.workspace import prepare_exercise_workspace


DEFAULT_CFLAGS = ["-Wall", "-Werror", "-Wextra"]


def extract_norminette_messages(output: str, stderr: str) -> list[str]:
    messages: list[str] = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("Setting locale to "):
            continue
        if stripped.endswith(": OK!"):
            continue
        messages.append(line)
    if stderr.strip():
        messages.append(stderr.rstrip())
    return messages


def exercise_progress_description(result: ExerciseResult) -> str:
    if result.status == "ok" and result.has_norminette_issues:
        return f"[orange3]{result.exercise_name}: NORM[/orange3]"
    if result.status == "ok":
        return f"[green]{result.exercise_name}: PASS[/green]"
    if result.status == "missing":
        return f"[yellow]{result.exercise_name}: MISSING[/yellow]"
    return f"[red]{result.exercise_name}: FAIL[/red]"


def norminette_command(assignment: str, exercise_name: str) -> list[str]:
    command = ["norminette"]
    if assignment == "C08" and exercise_name in {"ex01", "ex02"}:
        command.extend(["-R", "CheckDefine"])
    return command


def run_command(command: list[str], cwd: Path, timeout: float) -> CommandResult:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        return CommandResult(
            returncode=process.returncode,
            stdout=stdout,
            stderr=stderr,
        )
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
        return CommandResult(
            returncode=124,
            stdout=stdout,
            stderr=stderr,
            timed_out=True,
        )


def run_exercise(
    template_dir: Path,
    target_dir: Path,
    assignment: str,
    exercise_name: str,
    temp_root: Path,
    compiler: str,
    cflags: list[str],
    compile_timeout: float,
    run_timeout: float,
    run_norminette_checks: bool,
) -> ExerciseResult:
    source_test_dir = template_dir / "tests" / assignment / exercise_name
    source_test_files = sorted(source_test_dir.glob("*.c"))
    test_name = source_test_files[0].name if source_test_files else "(no test file)"
    result = ExerciseResult(exercise_name=exercise_name, test_name=test_name)

    if not source_test_files:
        result.status = "failed"
        result.errors.append(f"{exercise_name} has no test file.")
        return result

    unexpected_paths = unexpected_student_paths(target_dir, exercise_name, source_test_files)
    if unexpected_paths:
        result.extra_file_messages.append(
            "Unexpected files not in whitelist: "
            + ", ".join(path.as_posix() for path in unexpected_paths)
        )

    missing_paths = missing_student_paths(target_dir, exercise_name, source_test_files)
    if missing_paths:
        result.status = "missing"
        result.errors.append(
            "Skipped: missing exercise files: "
            + ", ".join(path.as_posix() for path in missing_paths)
        )
        return result

    if run_norminette_checks:
        norminette_result = run_command(
            command=norminette_command(assignment, exercise_name),
            cwd=target_dir / exercise_name,
            timeout=compile_timeout,
        )
        if norminette_result.timed_out:
            result.norminette_messages.append(
                f"norminette timed out after {compile_timeout:.1f}s."
            )
        else:
            norminette_messages = extract_norminette_messages(
                norminette_result.stdout,
                norminette_result.stderr,
            )
            if norminette_result.returncode != 0 and not norminette_messages:
                norminette_messages.append("norminette reported an error.")
            result.norminette_messages.extend(norminette_messages)

    _, workspace, test_files = prepare_exercise_workspace(
        template_dir=template_dir,
        target_dir=target_dir,
        assignment=assignment,
        exercise_name=exercise_name,
        temp_root=temp_root,
    )
    test_name = test_files[0].name if test_files else test_name
    result.test_name = test_name

    sanity_bin = test_files[0].with_suffix("").with_name("__mini_sanity__")
    sanity = run_command(
        command=[
            compiler,
            *cflags,
            "-o",
            str(sanity_bin),
            str(test_files[0]),
        ],
        cwd=workspace,
        timeout=compile_timeout,
    )
    result.checks += 1
    if sanity.timed_out:
        result.status = "failed"
        result.errors.append(
            f"{test_name} sanity compile timed out after {compile_timeout:.1f}s."
        )
        if sanity.stdout:
            result.errors.append(sanity.stdout.rstrip())
        if sanity.stderr:
            result.errors.append(sanity.stderr.rstrip())
        if sanity_bin.exists():
            sanity_bin.unlink()
        return result
    if sanity.returncode != 0:
        result.status = "failed"
        result.errors.append(f"{test_name} cannot compile.")
        if sanity.stderr:
            result.errors.append(sanity.stderr.rstrip())
        if sanity_bin.exists():
            sanity_bin.unlink()
        return result

    result.passed += 1
    if sanity_bin.exists():
        sanity_bin.unlink()

    for test_file in test_files:
        binary_path = test_file.with_suffix("")
        compile_result = run_command(
            command=[compiler, *cflags, "-o", str(binary_path), str(test_file)],
            cwd=workspace,
            timeout=compile_timeout,
        )
        result.checks += 1
        if compile_result.timed_out:
            result.status = "failed"
            result.errors.append(
                f"Compiling {test_file.name} timed out after {compile_timeout:.1f}s."
            )
            if compile_result.stdout:
                result.errors.append(compile_result.stdout.rstrip())
            if compile_result.stderr:
                result.errors.append(compile_result.stderr.rstrip())
            if binary_path.exists():
                binary_path.unlink()
            continue
        if compile_result.returncode != 0:
            result.status = "failed"
            result.errors.append(f"Failed to compile {test_file.name}.")
            if compile_result.stderr:
                result.errors.append(compile_result.stderr.rstrip())
            if binary_path.exists():
                binary_path.unlink()
            continue

        binary_rel = binary_path.relative_to(workspace)
        run_result = run_command(
            command=[f"./{binary_rel.as_posix()}"],
            cwd=workspace,
            timeout=run_timeout,
        )
        if run_result.timed_out:
            result.status = "failed"
            result.errors.append(f"{test_file.name} timed out after {run_timeout:.1f}s.")
            if run_result.stdout:
                result.errors.append(run_result.stdout.rstrip())
            if run_result.stderr:
                result.errors.append(run_result.stderr.rstrip())
            if binary_path.exists():
                binary_path.unlink()
            continue
        if run_result.returncode == 0:
            result.passed += 1
        else:
            result.status = "failed"
            result.errors.append(
                f"{test_file.name} exited with status {run_result.returncode}."
            )
            if run_result.stdout:
                result.errors.append(run_result.stdout.rstrip())
            if run_result.stderr:
                result.errors.append(run_result.stderr.rstrip())

        if binary_path.exists():
            binary_path.unlink()

    return result


def run_assignment_tests_parallel(
    template_dir: Path,
    target_dir: Path,
    temp_root: Path,
    assignment: str,
    compiler: str,
    cflags: list[str],
    jobs: int,
    compile_timeout: float,
    run_timeout: float,
    run_norminette_checks: bool,
    console: Console,
) -> tuple[list[ExerciseResult], int]:
    tests_root = template_dir / "tests"
    assignment_tests = tests_root / assignment

    if not assignment_tests.exists():
        raise FileNotFoundError(
            f"Sorry. Tests for {assignment} aren't available yet. "
            f"Available assignment tests: {available_assignments(tests_root)}"
        )

    exercise_names = sorted(path.name for path in assignment_tests.iterdir() if path.is_dir())
    if not exercise_names:
        return [], 0

    results: dict[str, ExerciseResult] = {}
    workers = max(1, min(jobs, len(exercise_names)))

    progress = Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )

    with progress:
        task_ids = {
            exercise_name: progress.add_task(f"[cyan]{exercise_name}: queued[/cyan]", total=1)
            for exercise_name in exercise_names
        }

        with ThreadPoolExecutor(max_workers=workers) as pool:
            future_map = {}
            for exercise_name in exercise_names:
                task_id = task_ids[exercise_name]
                future = pool.submit(
                    run_exercise,
                    template_dir,
                    target_dir,
                    assignment,
                    exercise_name,
                    temp_root,
                    compiler,
                    cflags,
                    compile_timeout,
                    run_timeout,
                    run_norminette_checks,
                )
                future_map[future] = (exercise_name, task_id)
            pending = set(future_map)
            running: set[str] = set()

            while pending:
                for future in pending:
                    exercise_name, task_id = future_map[future]
                    if future.running() and exercise_name not in running:
                        progress.update(
                            task_id,
                            description=f"[cyan]{exercise_name}: running[/cyan]",
                        )
                        running.add(exercise_name)

                done, pending = wait(pending, timeout=0.1, return_when=FIRST_COMPLETED)
                for future in done:
                    exercise_name, task_id = future_map[future]
                    try:
                        result = future.result()
                    except Exception as exc:
                        result = ExerciseResult(
                            exercise_name=exercise_name,
                            test_name="(internal error)",
                            status="failed",
                            errors=[f"Internal runner error: {exc}"],
                        )
                    results[exercise_name] = result
                    progress.update(
                        task_id,
                        description=exercise_progress_description(result),
                        completed=1,
                    )

    ordered_results = [results[exercise_name] for exercise_name in exercise_names]
    return ordered_results, len(exercise_names)
