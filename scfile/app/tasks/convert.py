"""Parallel file conversion task."""

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from scfile import convert, exceptions, types
from scfile.convert.types import Status
from scfile.options import Options
from scfile.utils import files

from .base import Context, Failure, Item, Progress, Started, Summary, TaskKind, failure, parallel


@dataclass(frozen=True, slots=True)
class Job:
    """Parameters for converting file sources."""

    kind: ClassVar[TaskKind] = TaskKind.CONVERT

    sources: tuple[types.SourceLike, ...]
    whitelist: tuple[str, ...]
    options: Options
    output: Path | None = None
    relative: bool = False
    parent: bool = False
    total: int | None = None
    workers: int | None = None

    def _convert(self, entry: types.FileEntry) -> Item | Failure:
        output = str(self.output) if self.output else None
        destination = files.destination(entry.relpath, self.relative, output)

        try:
            results = convert.auto(entry.path, destination, self.options)
            written = sum(result.status is Status.WRITTEN for result in results)
            skipped = len(results) - written
            return Item(
                source=entry.path,
                outputs=tuple(result.path for result in results),
                written=written,
                skipped=skipped,
            )
        except exceptions.ScFileException as error:
            return failure(entry.path, error)
        except Exception as error:
            return failure(entry.path, error, unexpected=True)

    def run(
        self,
        context: Context,
    ) -> Summary:
        """Convert matching files and report individual outcomes."""

        total = self.total
        if total is None:
            total = sum(
                1
                for _ in files.walk(
                    self.sources,
                    whitelist=self.whitelist,
                    parent=self.parent,
                )
            )

        entries = files.walk(self.sources, whitelist=self.whitelist, parent=self.parent)
        completed = succeeded = written = skipped = failed = 0
        output = self.output.resolve() if self.output else None
        context.emit(Started(self.kind, total, output))
        context.emit(Progress(0, total))

        for result in parallel(entries, self._convert, context, self.workers):
            completed += 1
            context.emit(result)

            if isinstance(result, Failure):
                failed += 1
            else:
                if result.written:
                    succeeded += 1
                written += result.written
                skipped += result.skipped

            context.emit(Progress(completed, total))

        return Summary(
            kind=self.kind,
            total=total,
            completed=completed,
            succeeded=succeeded,
            written=written,
            skipped=skipped,
            failed=failed,
            cancelled=context.stopped,
            output=output,
        )
