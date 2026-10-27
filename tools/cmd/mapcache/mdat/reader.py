import re
import struct
from hashlib import sha256
from pathlib import Path

import zstandard as zstd

from scfile.exceptions import DecodingError

from .models import XZ, Chunk, Entry, Frame, Header, Location, Note, Slice, view
from .versions import SUPPORTED_VERSIONS


SECTOR_SIZE = 4096
CHUNK_COUNT = 1024
MAX_PAYLOAD = 64 * 1024 * 1024
REGION_NAME = re.compile(r"reg\.(-?\d+)\.(-?\d+)\.mdat", re.IGNORECASE)


def coordinates(path: Path) -> XZ | None:
    match = REGION_NAME.fullmatch(path.name)
    return (int(match[1]), int(match[2])) if match else None


def paths(source: Path) -> list[Path]:
    return [source] if source.is_file() else sorted(source.rglob("*.mdat"))


def decompress(frame: Frame, notes: list[Note]) -> bytes | None:
    if frame.attempted:
        return frame.data

    frame.attempted = True

    if not frame.raw.complete:
        notes.append(Note("file", frame.raw.offset, "Compressed frame is truncated"))
        return None

    if not frame.raw.size:
        frame.data = b""
        return frame.data

    try:
        size = zstd.frame_content_size(frame.raw.data)
        if size != zstd.CONTENTSIZE_UNKNOWN and size > MAX_PAYLOAD:
            notes.append(Note("file", frame.raw.offset, f"Frame exceeds {MAX_PAYLOAD} decompressed bytes"))
            return None

        frame.data = zstd.ZstdDecompressor().decompress(
            frame.raw.data, max_output_size=MAX_PAYLOAD, allow_extra_data=False
        )

    except zstd.ZstdError as error:
        notes.append(Note("file", frame.raw.offset, str(error)))

    return frame.data


class Region:
    def __init__(self, path: Path, version: int | None = None):
        self.path = path.resolve()
        self.version = version or max(SUPPORTED_VERSIONS)
        if self.version not in SUPPORTED_VERSIONS:
            raise DecodingError(f"Unsupported MDAT version: {self.version}.", location=str(self.path))
        self.raw = memoryview(self.path.read_bytes())
        self.coordinates = coordinates(path)
        self.notes: list[Note] = []
        self.entries: list[Entry] = []
        match self.version:
            case 5:
                self._parse_v5()
            case 6:
                self._parse_v6()
            case 7:
                self._parse_v7()

    def _parse_v5(self) -> None:
        size = CHUNK_COUNT * 24
        if len(self.raw) < size:
            self.notes.append(Note("file", len(self.raw), "Incomplete location table"))
        table = self.raw[: min(len(self.raw) // 24, CHUNK_COUNT) * 24]
        for index, (sector, count, key) in enumerate(struct.iter_unpack(">ii16s", table)):
            self.entries.append(Entry(index, sector, count, key, view(self.raw, index * 24, 24)))

    def _parse_v6(self) -> None:
        size = CHUNK_COUNT * 24
        if len(self.raw) < size:
            self.notes.append(Note("file", len(self.raw), "Incomplete location table"))
        table = self.raw[: min(len(self.raw) // 24, CHUNK_COUNT) * 24]
        for index, (sector, count, key) in enumerate(struct.iter_unpack(">ii16s", table)):
            self.entries.append(Entry(index, sector, count, key, view(self.raw, index * 24, 24)))

    def _parse_v7(self) -> None:
        size = CHUNK_COUNT * 16
        if len(self.raw) < size:
            self.notes.append(Note("file", len(self.raw), "Incomplete location table"))
        table = self.raw[: min(len(self.raw) // 16, CHUNK_COUNT) * 16]
        for index, (sector, count, key) in enumerate(struct.iter_unpack(">ii8s", table)):
            self.entries.append(Entry(index, sector, count, key, view(self.raw, index * 16, 16)))

    @property
    def fingerprint(self) -> str:
        return sha256(self.raw).hexdigest()

    def location(self, index: int) -> Location:
        position = None
        if self.coordinates is not None:
            rx, rz = self.coordinates
            position = rx * 32 + index % 32, rz * 32 + index // 32
        return Location(self.path, self.coordinates, index, position)

    def chunk(self, index: int) -> Chunk:
        entry = self.entries[index]
        start = entry.sector * SECTOR_SIZE

        match self.version:
            case 5 | 6:
                header_size = 20
                table_end = CHUNK_COUNT * 24
            case 7:
                header_size = 28
                table_end = CHUNK_COUNT * 16

        chunk = Chunk(
            entry,
            self.location(index).chunk,
            view(self.raw, start, entry.sectors * SECTOR_SIZE),
            view(self.raw, start, header_size),
            self.version,
        )

        if not entry.present:
            return chunk

        if entry.sectors <= 0 or start < table_end or len(chunk.allocation.data) < header_size:
            chunk.notes.append(Note("file", start, "Chunk header is outside the data area"))
            return chunk

        match self.version:
            case 5 | 6:
                chunk.header = header = Header(*struct.unpack(">5i", chunk.header_raw.data))
            case 7:
                length, key, sections, additions, terrain, compressed = struct.unpack(">i8s4i", chunk.header_raw.data)
                chunk.header = header = Header(length, sections, additions, terrain, compressed, key)

        if header.section_mask & ~0xFFFF or header.add_mask & ~0xFFFF:
            chunk.notes.append(Note("file", start + 4, "Mask has bits outside 16 sections"))

        expected_sizes = (header.layout_size,)

        if self.version == 5:
            expected_sizes = (header.layout_size, header.layout_size + 20)

        if header.terrain_size not in expected_sizes:
            chunk.notes.append(Note("file", start, "Terrain size differs from mask layout"))

        if header.add_mask & ~header.section_mask & 0xFFFF:
            chunk.notes.append(Note("file", start, "Addition planes exist for absent sections"))

        if header.compressed_size < 0:
            chunk.notes.append(Note("file", start, "Negative compressed size"))
            return chunk

        chunk.terrain = Frame(
            Slice(
                start + header_size,
                header.compressed_size,
                chunk.allocation.data[header_size : header_size + header.compressed_size],
            )
        )

        if self.version >= 6:
            objects_offset = chunk.terrain.raw.end
            size = view(chunk.allocation.data, objects_offset - start, 4)

            if not size.complete:
                chunk.notes.append(Note("file", objects_offset, "Objects size is unavailable"))

            else:
                chunk.objects_size = struct.unpack(">i", size.data)[0]

                if chunk.objects_size < 0:
                    chunk.notes.append(Note("file", objects_offset, "Negative objects size"))

                else:
                    relative = objects_offset + 4 - start
                    chunk.objects = Frame(
                        Slice(
                            objects_offset + 4,
                            chunk.objects_size,
                            chunk.allocation.data[relative : relative + chunk.objects_size],
                        )
                    )

        if not chunk.allocation.complete:
            chunk.notes.append(Note("file", start, "Incomplete or negative sector allocation"))

        if chunk.physical_size is not None:
            if chunk.physical_size > chunk.allocation.size:
                chunk.notes.append(Note("file", start, "Stream extends beyond allocated sectors"))

            if self.version >= 6 and header.stream_length != chunk.physical_size - 3:
                chunk.notes.append(Note("file", start, "Stream length differs from encoded payload size"))

        return chunk
