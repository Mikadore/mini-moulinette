from __future__ import annotations

import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from mini_moul_app.discovery import resolve_assignment
from mini_moul_app.execution import run_assignment_tests_parallel, run_norminette
from mini_moul_app.reporting import print_summary
from mini_moul_app.workspace import create_temp_root


APP = typer.Typer(add_completion=False)


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

    repo_root = Path(__file__).resolve().parent.parent
    template_dir = repo_root / "mini-moul"
    start_time = time.time()

    resolved_assignment = resolve_assignment(assignment, target_dir)
    if not template_dir.exists():
        console.print("[red]mini-moul template directory is missing.[/red]")
        raise typer.Exit(1)

    temp_root: Optional[Path] = None
    try:
        temp_root = create_temp_root(workspace_root)
        if norminette:
            run_norminette(target_dir, console)
        console.print(
            f"Running tests for [bold]{resolved_assignment}[/bold] with [bold]{jobs}[/bold] worker(s)..."
        )
        results, questions = run_assignment_tests_parallel(
            template_dir=template_dir,
            target_dir=target_dir,
            temp_root=temp_root,
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
