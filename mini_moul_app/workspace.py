from __future__ import annotations

import shutil
import tempfile
from pathlib import Path


def copy_path(src: Path, dst: Path) -> None:
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def create_temp_root(workspace_root: Path) -> Path:
    return Path(tempfile.mkdtemp(prefix="mini-moul-", dir=workspace_root))


def prepare_exercise_workspace(
    template_dir: Path,
    target_dir: Path,
    assignment: str,
    exercise_name: str,
    temp_root: Path,
) -> tuple[Path, Path, list[Path]]:
    exercise_root = Path(tempfile.mkdtemp(prefix=f"{assignment}-{exercise_name}-", dir=temp_root))
    workspace = exercise_root / "mini-moul"
    test_src_dir = template_dir / "tests" / assignment / exercise_name
    test_dst_dir = workspace / "tests" / assignment / exercise_name

    copy_path(template_dir / "utils", workspace / "utils")
    copy_path(test_src_dir, test_dst_dir)

    student_dir = target_dir / exercise_name
    if student_dir.exists():
        copy_path(student_dir, exercise_root / exercise_name)

    return exercise_root, workspace, sorted(test_dst_dir.glob("*.c"))

