from __future__ import annotations

import time

from rich.console import Console

from mini_moul_app.models import ExerciseResult


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
        if result.status == "ok":
            result_parts.append(f"[green]{result.exercise_name}: OK[/green]")
            if not break_score:
                marks += 1
        elif result.status == "missing":
            result_parts.append(f"[yellow]{result.exercise_name}: MISSING[/yellow]")
            break_score = True
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

    missing = [result for result in results if result.status == "missing"]
    failed = [result for result in results if result.status == "failed"]
    if missing:
        console.print("")
        console.print("[bold yellow]Skipped exercises[/bold yellow]")
        for result in missing:
            console.print(f"[yellow]{result.exercise_name}/{result.test_name}[/yellow]")
            for error in result.errors:
                console.print(error)
            console.print("")
    if failed:
        console.print("")
        console.print("[bold red]Error report[/bold red]")
        for result in failed:
            console.print(f"[red]{result.exercise_name}/{result.test_name}[/red]")
            for error in result.errors:
                console.print(error)
            console.print("")

