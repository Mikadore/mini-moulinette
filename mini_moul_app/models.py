from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExerciseResult:
    exercise_name: str
    test_name: str
    status: str = "ok"
    errors: list[str] = field(default_factory=list)
    norminette_messages: list[str] = field(default_factory=list)
    compiler_warning_messages: list[str] = field(default_factory=list)
    extra_file_messages: list[str] = field(default_factory=list)
    checks: int = 0
    passed: int = 0

    @property
    def ok(self) -> bool:
        return self.status == "ok"

    @property
    def has_norminette_issues(self) -> bool:
        return bool(self.norminette_messages)

    @property
    def has_compiler_warnings(self) -> bool:
        return bool(self.compiler_warning_messages)

    @property
    def has_extra_files(self) -> bool:
        return bool(self.extra_file_messages)

    @property
    def has_warnings(self) -> bool:
        return (
            self.has_norminette_issues
            or self.has_compiler_warnings
            or self.has_extra_files
        )


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
