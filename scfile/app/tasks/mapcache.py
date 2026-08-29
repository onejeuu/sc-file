import traceback
from collections.abc import Iterator
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import ClassVar

from scfile import exceptions
from scfile.app.enums import TaskKind
from scfile.app.events import TaskError, TaskEvent, TaskItem, TaskItemFailure, TaskStarted
from scfile.convert import mapcache
from scfile.options import Options

from .base import Task, TaskContext
from .parallel import parallel


type MapCacheRegion = tuple[mapcache.Region, list[Path]]


@dataclass(frozen=True, slots=True)
class MapCacheTask(Task):
    kind: ClassVar[TaskKind] = TaskKind.MAPCACHE

    source: Path
    output: Path | None
    options: Options
    workers: int | None = None

    def _merge(self, region: MapCacheRegion, context: TaskContext) -> TaskItem | TaskItemFailure | None:
        key, paths = region
        output = self.output or self.source.with_name(f"{self.source.name}_mca")

        try:
            filename, chunks = mapcache.merge(key, paths, output, self.options, context.cancelled.is_set)
            return TaskItem(
                f"Region {key}",
                output / filename,
                f"{filename} merged {chunks} chunks",
            )

        except exceptions.MergeInterrupted:
            return None

        except exceptions.ScFileException as error:
            return TaskItemFailure(str(error.location or key), error)

        except OSError as error:
            return TaskItemFailure(str(error.filename or key), error)

        except Exception as error:
            return TaskItemFailure(f"Region {key}", error, traceback.format_exc())

    def run(
        self,
        context: TaskContext,
    ) -> Iterator[TaskEvent]:
        output = (self.output or self.source.with_name(f"{self.source.name}_mca")).resolve()

        result = mapcache.scan(self.source, context.cancelled.is_set)
        mapping = mapcache.group(result.paths)
        yield TaskStarted(self.kind, len(mapping), output)

        for error in result.errors:
            yield TaskError(error, source=error.filename)

        if not result.paths:
            if not result.errors:
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
