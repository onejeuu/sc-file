from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from scfile import exceptions
from scfile.app.enums import TaskKind
from scfile.app.events import TaskEvent, TaskItem, TaskStarted
from scfile.convert import mapmerge
from scfile.options import Options

from .base import Task, TaskContext


@dataclass(frozen=True, slots=True)
class MapMergeTask(Task):
    kind: ClassVar[TaskKind] = TaskKind.MAPMERGE

    sources: tuple[Path, ...]
    output: Path
    options: Options

    def run(self, context: TaskContext) -> Iterator[TaskEvent]:
        yield TaskStarted(self.kind, 1, self.output)

        try:
            tiles = mapmerge.collect(self.sources)
            if not tiles:
                location = str(self.sources[0]) if self.sources else None
                raise exceptions.ConversionError("No map tiles found.", location=location)

            result = mapmerge.render(
                tiles,
                self.output,
                self.options,
                context.cancelled.is_set,
            )

        except exceptions.MergeInterrupted:
            return

        yield TaskItem(str(self.sources[0]), result.output, f"Merged {result.tiles} tiles")
