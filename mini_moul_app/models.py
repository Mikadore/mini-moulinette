from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExerciseResult:
    exercise_name: str
    test_name: str
    status: str = "ok"
    errors: list[str] = field(default_factory=list)
    norminette_messages: list[str] = field(default_factory=list)
    checks: int = 0
    passed: int = 0

    @property
    def ok(self) -> bool:
        return self.status == "ok"

    @property
    def has_norminette_issues(self) -> bool:
        return bool(self.norminette_messages)


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
