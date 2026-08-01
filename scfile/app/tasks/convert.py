"""Parallel file conversion task."""

from dataclasses import dataclass
from pathlib import Path

from scfile import exceptions, types
from scfile.convert import files as conversion
from scfile.convert.types import Status
from scfile.options import ConvertOptions
from scfile.utils import files

from .base import Context, Failure, Item, Progress, Summary, failure, parallel


@dataclass(frozen=True, slots=True)
class Job:
    """Parameters for converting file sources."""

    sources: tuple[types.PathLike, ...]
    whitelist: tuple[str, ...]
    options: ConvertOptions
    output: Path | None = None
    relative: bool = False
    parent: bool = False
    total: int | None = None
    workers: int | None = None

    def _convert(self, entry: types.FileEntry) -> Item | Failure:
        output = str(self.output) if self.output else None
        destination = files.destination(entry.relpath, self.relative, output)

        try:
            results = conversion.auto(entry.path, destination, self.options)
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

        entries = files.walk(self.sources, whitelist=self.whitelist, parent=self.parent)
        completed = written = skipped = failed = 0
        context.emit(Progress(0, self.total))

        for result in parallel(entries, self._convert, context, self.workers):
            completed += 1
            context.emit(result)

            if isinstance(result, Failure):
                failed += 1
            else:
                written += result.written
                skipped += result.skipped

            context.emit(Progress(completed, self.total))

        return Summary(
            name="Converting",
            total=self.total if self.total is not None else completed,
            completed=completed,
            written=written,
            skipped=skipped,
            failed=failed,
            cancelled=context.stopped,
        )
