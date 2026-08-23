import traceback
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from scfile import exceptions, types
from scfile.app.enums import TaskKind
from scfile.app.events import TaskEvent, TaskItem, TaskItemFailure, TaskStarted
from scfile.options import Options

from .base import Task, TaskContext


type Operation = Callable[..., types.ResultPath]


@dataclass(frozen=True, slots=True)
class AnimateTask(Task):
    kind: ClassVar[TaskKind] = TaskKind.ANIMATE

    operation: Operation
    source: Path
    models: tuple[Path | None, ...]
    output: Path
    options: Options = field(default_factory=Options)

    def run(
        self,
        context: TaskContext,
    ) -> Iterator[TaskEvent]:
        output = self.output.resolve()
        yield TaskStarted(self.kind, 1, output)
        if context.stopped:
            return

        src = str(self.source)
        try:
            result = self.operation(self.source, *self.models, output=self.output, options=self.options)
            yield TaskItem(src, result)

        except exceptions.ScFileException as error:
            yield TaskItemFailure(src, error)

        except Exception as error:
            yield TaskItemFailure(src, error, traceback.format_exc())
