from collections.abc import Iterator
from pathlib import Path

from .mdat import objects
from .mdat.models import Chunk, Note, Objects
from .mdat.reader import Region, paths
from .reports import Diagnostic


def regions(source: Path, notes: list[Diagnostic]) -> Iterator[Region]:
    for path in paths(source):
        try:
            region = Region(path)
        except OSError as error:
            notes.append(Diagnostic(path, None, Note("file", 0, str(error))))
            continue
        notes.extend(Diagnostic(region.path, None, note) for note in region.notes)
        yield region


def chunks(source: Path, notes: list[Diagnostic]) -> Iterator[tuple[Region, Chunk]]:
    for region in regions(source, notes):
        for entry in region.entries:
            if entry.present:
                chunk = region.chunk(entry.index)
                notes.extend(Diagnostic(region.path, entry.index, note) for note in chunk.notes)
                yield region, chunk


def object_items(chunk: Chunk) -> Objects | None:
    if chunk.objects is None or chunk.objects.data is None:
        return None
    if chunk.objects_size == 0:
        return Objects(memoryview(b""), count=0)
    return objects.read(chunk.objects.data)
