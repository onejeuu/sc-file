from collections.abc import Iterator
from pathlib import Path

from .mdat import objects
from .mdat.models import Chunk, Note
from .mdat.objects import Objects
from .mdat.reader import Region, decompress, paths
from .reports import Diagnostic


def regions(source: Path, notes: list[Diagnostic], version: int | None = None) -> Iterator[Region]:
    for path in paths(source):
        try:
            region = Region(path, version)

        except OSError as error:
            notes.append(Diagnostic(path, None, Note("file", 0, str(error))))
            continue

        notes.extend(Diagnostic(region.path, None, note) for note in region.notes)
        yield region


def chunks(source: Path, notes: list[Diagnostic], version: int | None = None) -> Iterator[tuple[Region, Chunk]]:
    for region in regions(source, notes, version):
        for entry in region.entries:
            if entry.present:
                chunk = region.chunk(entry.index)
                yield region, chunk


def object_items(chunk: Chunk) -> Objects | None:
    if chunk.objects is None:
        return None
    if chunk.objects_size == 0:
        return Objects(memoryview(b""), count=0)
    data = decompress(chunk.objects, chunk.notes)
    return objects.read(data, chunk.version) if data is not None else None
