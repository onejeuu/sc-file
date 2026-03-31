import argparse
import json
import os
import re
import struct
import time
import zlib
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TypeAlias

from profiler import profiler

from scfile import formats
from scfile.core.context.content import RegionContent
from scfile.formats.mdat.decoder import NIBBLE_SIZE, SECTION_SIZE
from scfile.structures.region import RegionChunk


HEIGHT = 256

SECTION_COUNT = 16
SECTION = SECTION_SIZE

_CURRENT_TIME = int(time.time())
_TIMESTAMPS = struct.pack(">I", _CURRENT_TIME) * 1024

RegionKey: TypeAlias = tuple[int, int]


def nbt(tag: int, name: bytes, payload: bytes) -> bytes:
    return bytes([tag]) + struct.pack(">H", len(name)) + name + payload


def compound(name: bytes, *children: bytes) -> bytes:
    return nbt(0x0A, name, b"".join(children) + b"\x00")


def lst(name: bytes, typ: int, *items: bytes) -> bytes:
    return nbt(0x09, name, struct.pack(">bi", typ, len(items)) + b"".join(items))


def nbt_byte(name: bytes, v: int) -> bytes:
    return nbt(0x01, name, struct.pack(">b", v))


def nbt_int(name: bytes, v: int) -> bytes:
    return nbt(0x03, name, struct.pack(">i", v))


def nbt_long(name: bytes, v: int) -> bytes:
    return nbt(0x04, name, struct.pack(">q", v))


def nbt_ba(name: bytes, d: bytes) -> bytes:
    return nbt(0x07, name, struct.pack(">i", len(d)) + d)


def nbt_ia(name: bytes, a: tuple) -> bytes:
    return nbt(0x0B, name, struct.pack(f">i{len(a)}i", len(a), *a))


_VERSION = nbt_int(b"DataVersion", 1343)

_DUMMY_PAYLOAD = (
    nbt_long(b"LastUpdate", _CURRENT_TIME)
    + nbt_byte(b"TerrainPopulated", 1)
    + nbt_byte(b"LightPopulated", 1)
    + nbt_byte(b"V", 1)
    + nbt_long(b"InhabitedTime", 6000)
    + nbt_ia(b"HeightMap", tuple([6] * HEIGHT))
    + nbt_ba(b"Biomes", b"\x01" * HEIGHT)
    + lst(b"Entities", 0x0A)
    + lst(b"TileEntities", 0x0A)
    + lst(b"TileTicks", 0x0A)
)

_DUMMY_SECTIONS_PAYLOAD = (
    nbt_ba(b"Data", bytes(NIBBLE_SIZE))
    + nbt_ba(b"BlockLight", bytes(NIBBLE_SIZE))
    + nbt_ba(b"Add", bytes(NIBBLE_SIZE))
    + nbt_ba(b"SkyLight", b"\xff" * NIBBLE_SIZE)
    + b"\x00"
)


Sections: TypeAlias = dict[int, bytes]


def data_to_sections(data: bytes, mask: int, size: int) -> Sections:
    sections: Sections = {}

    present = [y for y in range(16) if (mask >> y) & 1]
    for idx, y in enumerate(present):
        sections[y] = data[idx * size : (idx + 1) * size]

    return sections


def section_payload(y: int, blocks: bytes) -> bytes:
    return nbt_byte(b"Y", y) + nbt_ba(b"Blocks", blocks) + _DUMMY_SECTIONS_PAYLOAD


def build_blocks_mapping(mapping: dict[int, int]) -> bytes:
    table = list(range(256))

    for old, new in mapping.items():
        table[old] = new

    return bytes(table)


def parse_blocks_mapping(path: Path | str) -> dict[int, int]:
    data = Path(path).read_text()
    data = re.sub(r"//.*", "", data)
    return {int(k): int(v) for k, v in json.loads(data).items()}


_ROOT = Path(__file__).parent
_BLOCKS_MAPPING = build_blocks_mapping(parse_blocks_mapping(_ROOT / "blocks.json"))


def chunk_nbt(cx: int, cz: int, chunk: RegionChunk, raw: bool = False) -> bytes:
    blocks = chunk.blocks

    if not raw:
        blocks = chunk.blocks.translate(_BLOCKS_MAPPING)

    blocks = data_to_sections(blocks, chunk.header.blocks_mask, SECTION_SIZE)
    sections = [section_payload(y, blocks[y]) for y in blocks.keys()]

    return compound(
        b"",
        _VERSION,
        compound(
            b"Level",
            nbt_int(b"xPos", cx),
            nbt_int(b"zPos", cz),
            lst(b"Sections", 0x0A, *sections),
            _DUMMY_PAYLOAD,
        ),
    )


def build_mca(out: Path | None, region: RegionContent, rx: int = 0, rz: int = 0, raw: bool = False) -> None:
    locations = bytearray(4096)
    timestamps = _TIMESTAMPS

    payload = [locations, timestamps]
    current_sector = len(payload)

    for chunk in region.chunks:
        lx, lz = chunk.index % 32, chunk.index // 32
        cx, cz = rx * 32 + lx, rz * 32 + lz

        compression_type = b"\x02"
        compressed_data = zlib.compress(chunk_nbt(cx, cz, chunk, raw), level=3)

        data = struct.pack(">I", len(compressed_data) + len(compression_type)) + compression_type + compressed_data

        total_bytes = len(data)
        sectors_needed = (total_bytes + 4096 - 1) // 4096

        idx = (lx + lz * 32) * 4
        locations[idx : idx + 4] = ((current_sector << 8) | sectors_needed).to_bytes(4, "big")

        payload.append(data)

        padding = (sectors_needed * 4096) - total_bytes
        payload.append(b"\x00" * padding)

        current_sector += sectors_needed

    if out:
        out.write_bytes(b"".join(payload))


def merge(item: tuple[RegionKey, list[Path]], output: Path, raw: bool = False) -> None:
    (rx, rz), paths = item

    merged = RegionContent()
    seen: set[int] = set()

    for path in paths:
        try:
            with formats.mdat.MdatDecoder(path) as mdat:
                region = mdat.decode()

            for chunk in region.chunks:
                if chunk.index not in seen:
                    merged.chunks.append(chunk)
                    seen.add(chunk.index)

        except Exception as err:
            print(f"ERROR: {path.name}: {err}")

    filename = f"r.{rx}.{rz}.mca"
    build_mca(output / filename, region=merged, rx=rx, rz=rz, raw=raw)
    print(f"{filename}: {len(merged.chunks)} chunks")


@profiler
def main() -> None:
    parser = argparse.ArgumentParser(description="Convert MDAT to MCA (1.12.2) format")
    parser.add_argument("source", type=Path, help="Source directory with MDAT files")
    parser.add_argument("output", type=Path, help="Output directory for MCA files")
    parser.add_argument("-w", "--workers", type=int, default=None, help="Number of worker threads (default: CPU count)")
    parser.add_argument("--raw", action="store_true", help="Raw blocks without lookup")

    args = parser.parse_args()

    source = args.source
    output = args.output
    output.mkdir(parents=True, exist_ok=True)

    mdats = [path for path in source.rglob("*.mdat") if path.stat().st_size > 0 and ".bck" not in str(path)]
    if not mdats:
        print(f"No MDAT files found in {source}")
        return

    regions: dict[RegionKey, list[Path]] = defaultdict(list)
    for path in mdats:
        rx, rz = map(int, path.stem.lstrip("reg.").split("."))
        regions[(rx, rz)].append(path)

    print(f"Found {len(regions)} unique regions")

    if args.workers is not None and args.workers <= 0:
        for item in regions.items():
            merge(item, args.output, args.raw)

    else:
        max_workers = (args.workers or os.cpu_count() or 4) * 2
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(lambda item: merge(item, output, args.raw), regions.items())

    print("Done.")


if __name__ == "__main__":
    main()
