"""Parallel map cache merging task."""

from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import ClassVar

from scfile import exceptions
from scfile.options import HandlerOptions
from scfile.utils import regions

from .base import Context, Failure, Item, Progress, Started, Summary, TaskKind, failure, parallel


type Region = tuple[regions.RegionKey, list[Path]]


@dataclass(frozen=True, slots=True)
class Job:
    """Parameters for merging map cache regions."""

    kind: ClassVar[TaskKind] = TaskKind.MAPCACHE

    source: Path
    output: Path | None
    options: HandlerOptions
    workers: int | None = None

    def _merge(self, region: Region, context: Context) -> Item | Failure | None:
        key, paths = region
        output = self.output or self.source.with_name(f"{self.source.name}_mca")

        try:
            filename, chunks = regions.merge(key, paths, output, self.options, context.cancelled)
            return Item(
                source=f"Region {key}",
                outputs=(output / filename,),
                written=1,
                detail=f"{filename} merged {chunks} chunks",
            )
        except exceptions.MergeInterrupted:
            return None
        except exceptions.ScFileException as error:
            return failure(str(error.location or key), error)
        except Exception as error:
            return failure(f"Region {key}", error, unexpected=True)

    def run(
        self,
        context: Context,
    ) -> Summary:
        """Merge discovered regions and report individual outcomes."""

        output = (self.output or self.source.with_name(f"{self.source.name}_mca")).resolve()
        paths = regions.resolve(self.source)
        if not paths:
            context.emit(Started(self.kind, 0, output))
            error = exceptions.RegionError("No MDAT files found.", location=str(self.source))
            context.emit(failure(str(self.source), error))
            return Summary(self.kind, 0, 0, failed=1, output=output)

        mapping = regions.parse(paths)
        if not mapping:
            context.emit(Started(self.kind, 0, output))
            error = exceptions.RegionError("No valid regions found.", location=str(self.source))
            context.emit(failure(str(self.source), error))
            return Summary(self.kind, 0, 0, failed=1, output=output)

        output.mkdir(parents=True, exist_ok=True)

        total = len(mapping)
        completed = succeeded = written = failed = 0
        context.emit(Started(self.kind, total, output))
        context.emit(Progress(0, total))
        operation = partial(self._merge, context=context)

        for result in parallel(mapping.items(), operation, context, self.workers):
            if result is None:
                continue

            completed += 1
            context.emit(result)
            if isinstance(result, Failure):
                failed += 1
            else:
                if result.written:
                    succeeded += 1
                written += result.written
            context.emit(Progress(completed, total))

        return Summary(
            kind=self.kind,
            total=total,
            completed=completed,
            succeeded=succeeded,
            written=written,
            failed=failed,
            cancelled=context.stopped,
            output=output,
        )
