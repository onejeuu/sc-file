from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from scfile import exceptions
from scfile.app.enums import TaskKind
from scfile.app.events import TaskEvent, TaskItem, TaskStarted
from scfile.convert import mapmerge
from scfile.convert.mapmerge import Tiles
from scfile.options import Options

from .base import Task, TaskContext


@dataclass(frozen=True, slots=True)
class MapMergeTask(Task):
    kind: ClassVar[TaskKind] = TaskKind.MAPMERGE

    tiles: Tiles
    output: Path
    options: Options

    def run(self, context: TaskContext) -> Iterator[TaskEvent]:
        yield TaskStarted(self.kind, 1, self.output)

        try:
            result = mapmerge.render(
                self.tiles,
                self.output,
                self.options,
                context.cancelled.is_set,
            )

        except exceptions.MergeInterrupted:
            return

        source = next(iter(self.tiles.values()))
        yield TaskItem(str(source), result.output, f"Merged {result.tiles} tiles")
