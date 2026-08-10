"""Parallel map cache merging task."""

import traceback
from collections.abc import Iterator
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import ClassVar

from scfile import exceptions
from scfile.app.enums import TaskKind
from scfile.app.events import TaskError, TaskEvent, TaskItem, TaskItemFailure, TaskStarted
from scfile.options import Options
from scfile.utils import regions

from .execution import Task, TaskContext
from .parallel import parallel


type Region = tuple[regions.RegionKey, list[Path]]


@dataclass(frozen=True, slots=True)
class MapCacheTask(Task):
    """Merge discovered map cache regions."""

    kind: ClassVar[TaskKind] = TaskKind.MAPCACHE

    source: Path
    output: Path | None
    options: Options
    workers: int | None = None

    def _merge(self, region: Region, context: TaskContext) -> TaskItem | TaskItemFailure | None:
        key, paths = region
        output = self.output or self.source.with_name(f"{self.source.name}_mca")

        try:
            filename, chunks = regions.merge(key, paths, output, self.options, context.cancelled)
            return TaskItem(
                f"Region {key}",
                output / filename,
                f"{filename} merged {chunks} chunks",
            )

        except exceptions.MergeInterrupted:
            return None

        except exceptions.ScFileException as error:
            return TaskItemFailure(str(error.location or key), error)

        except Exception as error:
            return TaskItemFailure(f"Region {key}", error, traceback.format_exc())

    def run(
        self,
        context: TaskContext,
    ) -> Iterator[TaskEvent]:
        """Yield merge results for discovered regions."""

        output = (self.output or self.source.with_name(f"{self.source.name}_mca")).resolve()

        paths = regions.resolve(self.source)
        mapping = regions.parse(paths)
        yield TaskStarted(self.kind, len(mapping), output)

        if not paths:
            yield TaskError(exceptions.RegionError("No MDAT files found.", location=str(self.source)))
            return

        if not mapping:
            yield TaskError(exceptions.RegionError("No valid regions found.", location=str(self.source)))
            return

        output.mkdir(parents=True, exist_ok=True)

        operation = partial(self._merge, context=context)
        for result in parallel(mapping.items(), operation, context, self.workers):
            if result is not None:
                yield result
