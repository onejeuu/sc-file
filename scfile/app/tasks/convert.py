import os
import traceback
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from hashlib import blake2s
from pathlib import Path
from typing import ClassVar

from scfile import convert, exceptions, types
from scfile.app import files
from scfile.app.enums import OutputLayout, TaskKind
from scfile.app.events import TaskError, TaskEvent, TaskItem, TaskItemFailure, TaskStarted
from scfile.enums import OnConflict
from scfile.formats import registry
from scfile.options import Options

from .execution import Task, TaskContext
from .parallel import parallel


type _ConvertItem = tuple[files.FileEntry, Path | None]
type _OutputOwner = tuple[Path, str]


def _normalize(path: types.PathLike) -> str:
    return os.path.normcase(os.path.abspath(path))


def _hashed(output: Path, source: str) -> Path:
    path = _normalize(source)
    digest = blake2s(path.encode("utf-8"), digest_size=6).hexdigest()
    return output.with_name(f"{output.stem}~{digest}{output.suffix}")


def _directory(
    entry: files.FileEntry,
    output: Path | None,
    layout: OutputLayout,
) -> str | None:
    match layout:
        case OutputLayout.DUMP:
            base = None
        case OutputLayout.RELATIVE:
            base = entry.root
        case OutputLayout.ROOTED:
            base = os.path.dirname(entry.root)

    return files.destination(entry.path, base, str(output) if output else None)


def _outputs(
    entries: Iterable[files.FileEntry | TaskError],
    output: Path | None,
    layout: OutputLayout,
    options: Options,
    collisions: dict[str, _OutputOwner],
) -> Iterator[_ConvertItem | TaskError]:
    """Assign output paths while scanning sources."""

    owners: dict[str, _OutputOwner] = {}
    assigned: set[Path] = set()

    for item in entries:
        if isinstance(item, TaskError):
            yield item
            continue

        decoder = registry.match(item.path)
        if decoder is None:
            error = exceptions.UnknownFormatError(item.path, Path(item.path).suffix)
            yield TaskError(error, source=item.path)
            continue

        source = Path(item.path)
        suffix = options.targets[decoder.content_type].suffix
        directory = _directory(item, output, layout)
        candidate = convert.paths.destination(source, directory, suffix)
        key = _normalize(candidate)

        if options.on_conflict is not OnConflict.REPLACE:
            destination = convert.paths.select(candidate, options, assigned)
            if destination is not None:
                assigned.add(destination)
            yield item, destination
            continue

        if owner := owners.get(key):
            destination = _hashed(candidate, item.path)
            collisions.setdefault(key, owner)
        else:
            destination = candidate
            owners[key] = (candidate, item.path)

        yield item, destination


def _cleanup(
    collisions: Iterable[_OutputOwner],
    published: set[str],
) -> Iterator[TaskError]:
    """Remove stale hashes after their source claimed the clean name."""

    for output, source in collisions:
        if _normalize(output) not in published:
            continue

        stale = _hashed(output, source)
        try:
            stale.unlink(missing_ok=True)

        except OSError as error:
            yield TaskError(error, source=str(stale))


@dataclass(frozen=True, slots=True)
class ConvertTask(Task):
    kind: ClassVar[TaskKind] = TaskKind.CONVERT

    sources: tuple[types.SourceLike, ...]
    filters: tuple[str, ...]
    options: Options
    output: Path | None = None
    layout: OutputLayout = OutputLayout.ROOTED
    total: int | None = None
    workers: int | None = None
    filtered: bool = False

    def _convert(
        self,
        item: _ConvertItem,
    ) -> TaskItem | TaskItemFailure:
        entry, destination = item
        if destination is None:
            return TaskItem(entry.path)

        try:
            result = convert.auto(entry.path, destination, self.options)
            return TaskItem(entry.path, result)

        except exceptions.ScFileException as error:
            return TaskItemFailure(entry.path, error)

        except Exception as error:
            return TaskItemFailure(entry.path, error, traceback.format_exc())

    def run(
        self,
        context: TaskContext,
    ) -> Iterator[TaskEvent]:
        output = self.output.resolve() if self.output else None
        total = self.total if self.total is not None else files.count(self.sources, self.filters)
        yield TaskStarted(self.kind, total, output, self.filtered)

        collisions: dict[str, _OutputOwner] = {}
        entries = files.scan(self.sources, filters=self.filters)
        outputs = _outputs(entries, output, self.layout, self.options, collisions)
        published: set[str] = set()

        for event in parallel(outputs, self._convert, context, self.workers):
            if isinstance(event, TaskItem) and event.output is not None:
                published.add(_normalize(event.output))
            yield event

        if not context.stopped and self.options.on_conflict is OnConflict.REPLACE:
            yield from _cleanup(collisions.values(), published)
