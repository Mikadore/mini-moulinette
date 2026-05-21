#!/usr/bin/env python3
"""Python CLI runner for mini-moulinette tests."""

from __future__ import annotations

import os
import re
import signal
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn


ASSIGNMENT_PATTERN = re.compile(r"^C(0[0-9]|1[0-3])$")
APP = typer.Typer(add_completion=False)


@dataclass
class ExerciseResult:
    exercise_name: str
    test_name: str
    ok: bool
    errors: list[str] = field(default_factory=list)
    checks: int = 0
    passed: int = 0


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


def resolve_assignment(requested: Optional[str], target_dir: Path) -> str:
    assignment = requested or target_dir.name
    if not ASSIGNMENT_PATTERN.match(assignment):
        raise typer.BadParameter(f"Invalid assignment '{assignment}'. Expected C00..C13.")
    if target_dir.name != assignment:
        raise typer.BadParameter(
            f"Directory name mismatch: target is '{target_dir.name}', assignment is '{assignment}'. "
            "Run inside the matching assignment directory or pass a matching --target."
        )
    return assignment


def copy_tree(src: Path, dst: Path) -> None:
    for child in src.iterdir():
        dst_child = dst / child.name
        if child.is_dir():
            shutil.copytree(child, dst_child)
        else:
            shutil.copy2(child, dst_child)


def prepare_workspace(
    template_dir: Path, target_dir: Path, workspace_root: Path
) -> tuple[Path, Path]:
    temp_root = Path(tempfile.mkdtemp(prefix="mini-moul-", dir=workspace_root))
    workspace = temp_root / "mini-moul"
    workspace.mkdir(parents=True, exist_ok=True)
    copy_tree(template_dir, workspace)

    # Copy student sources into temp root so existing relative includes keep working.
    for child in target_dir.iterdir():
        dst_child = temp_root / child.name
        if child.is_dir():
            shutil.copytree(child, dst_child, dirs_exist_ok=True)
        else:
            shutil.copy2(child, dst_child)
    return temp_root, workspace


def available_assignments(tests_root: Path) -> str:
    names = sorted(p.name for p in tests_root.iterdir() if p.is_dir())
    return " ".join(names)


def run_norminette(target_dir: Path, console: Console) -> None:
    if shutil.which("norminette") is None:
        console.print("norminette not found, skipping norminette checks")
        return
    console.print("[cyan]Running norminette...[/cyan]")
    subprocess.run(["norminette"], cwd=target_dir, check=False)


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
    exercise_dir: Path,
    workspace: Path,
    compiler: str,
    compile_timeout: float,
    run_timeout: float,
) -> ExerciseResult:
    test_files = sorted(exercise_dir.glob("*.c"))
    exercise_name = exercise_dir.name
    test_name = test_files[0].name if test_files else "(no test file)"
    result = ExerciseResult(exercise_name=exercise_name, test_name=test_name, ok=True)

    if not test_files:
        result.ok = False
        result.errors.append(f"{exercise_name} has no test file.")
        return result

    sanity_bin = exercise_dir / "__mini_sanity__"
    sanity = run_command(
        command=[
            compiler,
            "-Wall",
            "-Werror",
            "-Wextra",
            "-o",
            str(sanity_bin),
            str(test_files[0]),
        ],
        cwd=workspace,
        timeout=compile_timeout,
    )
    result.checks += 1
    if sanity.timed_out:
        result.ok = False
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
        result.ok = False
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
            command=[compiler, "-o", str(binary_path), str(test_file)],
            cwd=workspace,
            timeout=compile_timeout,
        )
        result.checks += 1
        if compile_result.timed_out:
            result.ok = False
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
            result.ok = False
            result.errors.append(f"Failed to compile {test_file.name}.")
            if compile_result.stderr:
                result.errors.append(compile_result.stderr.rstrip())
            if binary_path.exists():
                binary_path.unlink()
            continue

        run_result = run_command(
            command=[f"./{binary_path.name}"],
            cwd=test_file.parent,
            timeout=run_timeout,
        )
        if run_result.timed_out:
            result.ok = False
            result.errors.append(
                f"{test_file.name} timed out after {run_timeout:.1f}s."
            )
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
            result.ok = False
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
    workspace: Path,
    assignment: str,
    compiler: str,
    jobs: int,
    compile_timeout: float,
    run_timeout: float,
    console: Console,
) -> tuple[list[ExerciseResult], int]:
    tests_root = workspace / "tests"
    assignment_tests = tests_root / assignment

    if not assignment_tests.exists():
        raise FileNotFoundError(
            f"Sorry. Tests for {assignment} aren't available yet. "
            f"Available assignment tests: {available_assignments(tests_root)}"
        )

    exercise_dirs = sorted(p for p in assignment_tests.iterdir() if p.is_dir())
    if not exercise_dirs:
        return [], 0

    results: dict[str, ExerciseResult] = {}
    workers = max(1, min(jobs, len(exercise_dirs)))

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
            exercise_dir.name: progress.add_task(
                f"[cyan]{exercise_dir.name}: queued[/cyan]", total=1
            )
            for exercise_dir in exercise_dirs
        }

        with ThreadPoolExecutor(max_workers=workers) as pool:
            future_map = {}
            for exercise_dir in exercise_dirs:
                task_id = task_ids[exercise_dir.name]
                future = pool.submit(
                    run_exercise,
                    exercise_dir,
                    workspace,
                    compiler,
                    compile_timeout,
                    run_timeout,
                )
                future_map[future] = (exercise_dir.name, task_id)
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
                            ok=False,
                            errors=[f"Internal runner error: {exc}"],
                        )
                    results[exercise_name] = result
                    if result.ok:
                        progress.update(
                            task_id,
                            description=f"[green]{exercise_name}: PASS[/green]",
                            completed=1,
                        )
                    else:
                        progress.update(
                            task_id,
                            description=f"[red]{exercise_name}: FAIL[/red]",
                            completed=1,
                        )

    ordered_results = [results[exercise_dir.name] for exercise_dir in exercise_dirs]
    return ordered_results, len(exercise_dirs)


def print_summary(
    assignment: str,
    results: list[ExerciseResult],
    questions: int,
    start_time: float,
    console: Console,
) -> None:
    marks = 0
    break_score = False
    result_parts: list[str] = []
    checks = sum(result.checks for result in results)
    passed = sum(result.passed for result in results)

    for result in results:
        if result.ok:
            result_parts.append(f"[green]{result.exercise_name}: OK[/green]")
            if not break_score:
                marks += 1
        else:
            result_parts.append(f"[red]{result.exercise_name}: KO[/red]")
            break_score = True

    percent = (100 * marks // questions) if questions else 0
    status = "[green]passed[/green]" if percent >= 50 else "[red]FAILED[/red]"
    score = f"[green]{percent}/100[/green]" if percent >= 50 else f"[red]{percent}/100[/red]"
    elapsed = int(time.time() - start_time)

    console.print("")
    console.print("[bold cyan]mini v2 by Mikadore[/bold cyan]")
    console.print(f"Assignment: [bold]{assignment}[/bold]")
    console.print(f"Checks: {passed}/{checks} passed")
    console.print(f"Result: {', '.join(result_parts)}")
    console.print(f"Final score: {score}")
    console.print(f"Status: {status}")
    console.print(f"[dim]Test completed in {elapsed}s.[/dim]")

    failed = [result for result in results if not result.ok]
    if failed:
        console.print("")
        console.print("[bold red]Error report[/bold red]")
        for result in failed:
            console.print(f"[red]{result.exercise_name}/{result.test_name}[/red]")
            for error in result.errors:
                console.print(error)
            console.print("")


@APP.command()
def main(
    assignment: Optional[str] = typer.Argument(
        None,
        help="Assignment name (C00..C13). Defaults to current directory name.",
    ),
    target: Optional[Path] = typer.Option(
        None,
        "--target",
        "-t",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Assignment directory to run tests in.",
    ),
    compiler: str = typer.Option(
        "cc",
        "--compiler",
        "-c",
        help="C compiler command used to build tests.",
    ),
    jobs: int = typer.Option(
        max(1, (os.cpu_count() or 1) // 2),
        "--jobs",
        "-j",
        min=1,
        help="Number of exercises to process in parallel.",
    ),
    compile_timeout: float = typer.Option(
        10.0,
        "--compile-timeout",
        min=0.1,
        help="Maximum time allowed for each compile step in seconds.",
    ),
    run_timeout: float = typer.Option(
        10.0,
        "--run-timeout",
        min=0.1,
        help="Maximum time allowed for each test binary execution in seconds.",
    ),
    workspace_root: Path = typer.Option(
        Path(tempfile.gettempdir()),
        "--workspace-root",
        dir_okay=True,
        file_okay=False,
        resolve_path=True,
        help="Directory where the temporary workspace is created (defaults to /tmp).",
    ),
    norminette: bool = typer.Option(
        True,
        "--norminette/--no-norminette",
        help="Run norminette before tests when available.",
    ),
    keep_workspace: bool = typer.Option(
        False,
        "--keep-workspace",
        help="Keep generated temporary test workspace for debugging.",
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        help="Disable colored output.",
    ),
) -> None:
    console = Console(no_color=no_color)
    target_dir = (target or Path.cwd()).resolve()
    if not target_dir.exists() or not target_dir.is_dir():
        console.print(f"[red]Invalid target directory: {target_dir}[/red]")
        raise typer.Exit(1)
    if not workspace_root.exists() or not workspace_root.is_dir():
        console.print(f"[red]Invalid workspace root: {workspace_root}[/red]")
        raise typer.Exit(1)

    repo_root = Path(__file__).resolve().parent
    template_dir = repo_root / "mini-moul"
    start_time = time.time()

    resolved_assignment = resolve_assignment(assignment, target_dir)
    if not template_dir.exists():
        console.print("[red]mini-moul template directory is missing.[/red]")
        raise typer.Exit(1)

    temp_root: Optional[Path] = None
    workspace: Optional[Path] = None
    try:
        temp_root, workspace = prepare_workspace(template_dir, target_dir, workspace_root)
        if norminette:
            run_norminette(target_dir, console)
        console.print(
            f"Running tests for [bold]{resolved_assignment}[/bold] with [bold]{jobs}[/bold] worker(s)..."
        )
        results, questions = run_assignment_tests_parallel(
            workspace=workspace,
            assignment=resolved_assignment,
            compiler=compiler,
            jobs=jobs,
            compile_timeout=compile_timeout,
            run_timeout=run_timeout,
            console=console,
        )
        print_summary(
            assignment=resolved_assignment,
            results=results,
            questions=questions,
            start_time=start_time,
            console=console,
        )
    except KeyboardInterrupt:
        console.print("[red]Script aborted by user. Cleaning up...[/red]")
        raise typer.Exit(130)
    except FileNotFoundError as err:
        console.print(f"[red]{err}[/red]")
        raise typer.Exit(1)
    finally:
        if temp_root is not None and temp_root.exists() and not keep_workspace:
            shutil.rmtree(temp_root)


def cli() -> None:
    APP()


if __name__ == "__main__":
    cli()
