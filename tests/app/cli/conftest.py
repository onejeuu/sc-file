from collections.abc import Callable
from typing import Any

import pytest

from scfile.app.enums import TaskKind
from scfile.app.events import TaskSummary


class Feedback:
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.summary: TaskSummary | None = None

    def finish(self, summary: TaskSummary) -> None:
        self.summary = summary


@pytest.fixture
def command_runner(monkeypatch: pytest.MonkeyPatch) -> Callable[[Any, TaskKind, bool], list[Any]]:
    def install(module: Any, kind: TaskKind, failed: bool = False) -> list[Any]:
        tasks: list[Any] = []

        def execute(task: Any, feedback: Any) -> TaskSummary:
            tasks.append(task)
            summary = TaskSummary(kind)
            if failed:
                summary.work.failed = 1
            return summary

        monkeypatch.setattr(module, "execute", execute)
        monkeypatch.setattr(module, "TaskFeedback", Feedback)
        return tasks

    return install
