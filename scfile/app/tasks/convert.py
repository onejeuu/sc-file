"""Parallel file conversion task."""

import os
import traceback
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from scfile import convert, exceptions, types
from scfile.app.enums import OutputLayout, TaskKind
from scfile.options import Options
from scfile.utils import files

from .events import TaskEvent, TaskFailure, TaskItem, TaskStarted
from .execution import Task, TaskContext
from .parallel import parallel


@dataclass(frozen=True, slots=True)
class ConvertTask(Task):
    """Convert matching file sources."""

    kind: ClassVar[TaskKind] = TaskKind.CONVERT

    sources: tuple[types.SourceLike, ...]
    filters: tuple[str, ...]
    options: Options
    output: Path | None = None
    layout: OutputLayout = OutputLayout.FLAT
    total: int | None = None
    workers: int | None = None

    def _convert(self, entry: types.FileEntry) -> TaskItem | TaskFailure:
        output = str(self.output) if self.output else None
        match self.layout:
            case OutputLayout.FLAT:
                base = None
            case OutputLayout.RELATIVE:
                base = entry.root
            case OutputLayout.ROOTED:
                base = os.path.dirname(entry.root)

        destination = files.destination(entry.path, base, output)

        try:
            result = convert.auto(entry.path, destination, self.options)
            return TaskItem(entry.path, result)

        except exceptions.ScFileException as error:
            return TaskFailure(entry.path, error)

        except Exception as error:
            return TaskFailure(entry.path, error, traceback.format_exc())

    def run(
        self,
        context: TaskContext,
    ) -> Iterator[TaskEvent]:
        """Yield conversion results for matching files."""

        output = self.output.resolve() if self.output else None
        total = self.total if self.total is not None else files.count(self.sources, self.filters)
        yield TaskStarted(self.kind, total, output)

        entries = files.walk(self.sources, filters=self.filters)
        yield from parallel(entries, self._convert, context, self.workers)
