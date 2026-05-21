from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import typer


ASSIGNMENT_PATTERN = re.compile(r"^C(0[0-9]|1[0-3])$")
STUDENT_REF_PATTERN = re.compile(
    r"(?:\.\./)+(ex\d{2}/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*)"
)


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


def available_assignments(tests_root: Path) -> str:
    names = sorted(path.name for path in tests_root.iterdir() if path.is_dir())
    return " ".join(names)


def collect_student_refs(test_files: list[Path]) -> list[Path]:
    refs: set[Path] = set()
    for test_file in test_files:
        content = test_file.read_text(errors="replace")
        refs.update(Path(match) for match in STUDENT_REF_PATTERN.findall(content))
    return sorted(refs)


def whitelisted_student_paths(exercise_name: str, test_files: list[Path]) -> list[Path]:
    return sorted(
        ref
        for ref in collect_student_refs(test_files)
        if ref.parts and ref.parts[0] == exercise_name
    )


def missing_student_paths(
    target_dir: Path, exercise_name: str, test_files: list[Path]
) -> list[Path]:
    refs = whitelisted_student_paths(exercise_name, test_files)
    if refs:
        return sorted(ref for ref in refs if not (target_dir / ref).exists())

    exercise_dir = target_dir / exercise_name
    if not exercise_dir.exists():
        return [Path(exercise_name)]
    return []


def unexpected_student_paths(
    target_dir: Path, exercise_name: str, test_files: list[Path]
) -> list[Path]:
    exercise_dir = target_dir / exercise_name
    if not exercise_dir.exists():
        return []

    refs = whitelisted_student_paths(exercise_name, test_files)
    if not refs:
        return []

    actual_files = {
        Path(exercise_name) / path.relative_to(exercise_dir)
        for path in exercise_dir.rglob("*")
        if path.is_file()
    }
    return sorted(actual_files - set(refs))
