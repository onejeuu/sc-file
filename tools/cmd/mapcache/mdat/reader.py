import re
import struct
from hashlib import sha256
from pathlib import Path

import zstandard as zstd

from .models import Chunk, Entry, Frame, Header, Location, Note, XZ, view


SECTOR_SIZE = 4096
TABLE_SIZE = 24576
ENTRY_SIZE = 24
REGION_NAME = re.compile(r"reg\.(-?\d+)\.(-?\d+)\.mdat", re.IGNORECASE)
MAX_PAYLOAD = 64 * 1024 * 1024


def coordinates(path: Path) -> XZ | None:
    match = REGION_NAME.fullmatch(path.name)
    return (int(match[1]), int(match[2])) if match else None


def paths(source: Path) -> list[Path]:
    return [source] if source.is_file() else sorted(source.rglob("*.mdat"))


def decompress(frame: Frame, notes: list[Note]) -> None:
    try:
        size = zstd.frame_content_size(frame.raw.data)
        if size != zstd.CONTENTSIZE_UNKNOWN and size > MAX_PAYLOAD:
            notes.append(Note("file", frame.raw.offset, f"Frame exceeds {MAX_PAYLOAD} decompressed bytes"))
            return
        context = zstd.ZstdDecompressor()
        if size == zstd.CONTENTSIZE_UNKNOWN:
            # Bound unknown-size frames before inspecting their consumed bytes.
            frame.data = context.decompress(frame.raw.data, max_output_size=MAX_PAYLOAD)
        decoder = context.decompressobj()
        result = decoder.decompress(frame.raw.data)
        if not decoder.eof:
            notes.append(Note("file", frame.raw.offset, "Incomplete Zstandard frame"))
            return
        frame.data = result
        if decoder.unused_data:
            notes.append(Note("file", frame.raw.end - len(decoder.unused_data), "Bytes remain after the first frame"))
    except zstd.ZstdError as error:
        notes.append(Note("file", frame.raw.offset, str(error)))


class Region:
    def __init__(self, path: Path):
        self.path = path.resolve()
        self.raw = memoryview(self.path.read_bytes())
        self.coordinates = coordinates(path)
        self.notes: list[Note] = []
        self.entries: list[Entry] = []
        if len(self.raw) < TABLE_SIZE:
            self.notes.append(Note("file", len(self.raw), "Incomplete location table"))
        for index in range(min(1024, len(self.raw) // ENTRY_SIZE)):
            raw = view(self.raw, index * ENTRY_SIZE, ENTRY_SIZE)
            sector, count, a, b, c, d = struct.unpack(">6i", raw.data)
            self.entries.append(Entry(index, sector, count, (a, b, c, d), raw))

    @property
    def fingerprint(self) -> str:
        return sha256(self.raw).hexdigest()

    def location(self, index: int) -> Location:
        position = None
        if self.coordinates is not None:
            rx, rz = self.coordinates
            position = rx * 32 + index % 32, rz * 32 + index // 32
        return Location(self.path, self.coordinates, index, position)

    def chunk(self, index: int, *, decode: bool = True) -> Chunk:
        entry = self.entries[index]
        start = entry.sector * SECTOR_SIZE
        chunk = Chunk(
            entry,
            self.location(index).chunk,
            view(self.raw, start, entry.sectors * SECTOR_SIZE),
            view(self.raw, start, 20),
        )
        if not entry.present:
            return chunk
        if start < TABLE_SIZE or not chunk.header_raw.complete:
            chunk.notes.append(Note("file", start, "Chunk header is outside the data area"))
            return chunk
        chunk.header = header = Header(*struct.unpack(">5i", chunk.header_raw.data))
        if header.section_mask & ~0xFFFF or header.add_mask & ~0xFFFF:
            chunk.notes.append(Note("file", start + 4, "Mask has bits outside 16 sections"))
        if header.terrain_size != header.layout_size:
            chunk.notes.append(
                Note("file", start + 12, f"Terrain size differs from mask layout ({header.layout_size})")
            )
        if header.add_mask & ~header.section_mask & 0xFFFF:
            chunk.notes.append(Note("file", start + 8, "Addition planes exist for absent sections"))
        if header.compressed_size < 0:
            chunk.notes.append(Note("file", start + 16, "Negative compressed size"))
            return chunk
        chunk.terrain = Frame(view(self.raw, start + 20, header.compressed_size))
        objects_offset = chunk.terrain.raw.end
        size = view(self.raw, objects_offset, 4)
        if not size.complete:
            chunk.notes.append(Note("file", objects_offset, "Objects size is unavailable"))
        else:
            chunk.objects_size = struct.unpack(">i", size.data)[0]
            if chunk.objects_size < 0:
                chunk.notes.append(Note("file", objects_offset, "Negative objects size"))
            else:
                chunk.objects = Frame(view(self.raw, objects_offset + 4, chunk.objects_size))
                physical = header.compressed_size + chunk.objects_size + 24
                if header.stream_length != physical - 3:
                    chunk.notes.append(Note("file", start, "Length differs from compressed + objects + 21"))
                if entry.sectors != (physical + SECTOR_SIZE - 1) // SECTOR_SIZE:
                    chunk.notes.append(Note("file", entry.raw.offset + 4, "Sector count differs from physical size"))
        if not chunk.allocation.complete:
            chunk.notes.append(Note("file", start, "Incomplete or negative sector allocation"))
        if chunk.physical_size is not None and chunk.physical_size > chunk.allocation.size:
            chunk.notes.append(Note("file", start, "Stream extends beyond allocated sectors"))
        if decode:
            decompress(chunk.terrain, chunk.notes)
            if chunk.objects is not None:
                if chunk.objects_size == 0:
                    chunk.objects.data = b""
                else:
                    decompress(chunk.objects, chunk.notes)
        return chunk
