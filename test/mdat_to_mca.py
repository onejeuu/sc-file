import argparse
import json
import os
import re
import time
import zlib
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from struct import pack
from typing import TypeAlias

from profiler import profiler

from scfile import formats
from scfile.core.context.content import RegionContent
from scfile.formats.nbt.enums import Tag
from scfile.structures.region import RegionChunk


HEIGHT = 256
SECTION_COUNT = 16

_CURRENT_TIME = int(time.time())
_TIMESTAMPS = pack(">I", _CURRENT_TIME) * 1024

RegionKey: TypeAlias = tuple[int, int]


def _tag(tag_type: int, name: bytes) -> bytes:
    return bytes([tag_type]) + pack(">H", len(name)) + name


_VERSION = _tag(Tag.INT, b"DataVersion") + pack(">i", 1343)  # Anvil 1.12.2
_LEVEL_HEAD = _tag(Tag.COMPOUND, b"Level")
_XPOS_HEAD = _tag(Tag.INT, b"xPos")
_ZPOS_HEAD = _tag(Tag.INT, b"zPos")
_SECTIONS_HEAD = _tag(Tag.LIST, b"Sections")
_Y_HEAD = _tag(Tag.BYTE, b"Y")
_BLOCKS_HEAD = _tag(Tag.BYTE_ARRAY, b"Blocks")
_END = b"\x00"

_Y_PACKED = [pack(">b", y) for y in range(SECTION_COUNT)]


_DUMMY_CHUNK_PAYLOAD = b"".join(
    [
        _tag(Tag.LONG, b"LastUpdate") + pack(">q", _CURRENT_TIME),
        _tag(Tag.BYTE, b"TerrainPopulated") + pack(">b", 1),
        _tag(Tag.BYTE, b"LightPopulated") + pack(">b", 1),
        _tag(Tag.BYTE, b"V") + pack(">b", 1),
        _tag(Tag.LONG, b"InhabitedTime") + pack(">q", 6000),
        _tag(Tag.INT_ARRAY, b"HeightMap") + pack(">i", HEIGHT) + pack(f">{HEIGHT}i", *([6] * HEIGHT)),
        _tag(Tag.BYTE_ARRAY, b"Biomes") + pack(">i", HEIGHT) + (b"\x01" * HEIGHT),
        _tag(Tag.LIST, b"Entities") + pack(">b", Tag.COMPOUND) + pack(">i", 0),
        _tag(Tag.LIST, b"TileEntities") + pack(">b", Tag.COMPOUND) + pack(">i", 0),
        _tag(Tag.LIST, b"TileTicks") + pack(">b", Tag.COMPOUND) + pack(">i", 0),
    ]
)

_DUMMY_SECTIONS_PAYLOAD = b"".join(
    [
        _tag(Tag.BYTE_ARRAY, b"Data") + pack(">i", 2048) + bytes(2048),
        _tag(Tag.BYTE_ARRAY, b"BlockLight") + pack(">i", 2048) + bytes(2048),
        _tag(Tag.BYTE_ARRAY, b"Add") + pack(">i", 2048) + bytes(2048),
        _tag(Tag.BYTE_ARRAY, b"SkyLight") + pack(">i", 2048) + (b"\xff" * 2048),
        _END,
    ]
)


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
    blocks = chunk.blocks if raw else chunk.blocks.translate(_BLOCKS_MAPPING)
    mask = chunk.header.blocks_mask

    present = [y for y in range(16) if (mask >> y) & 1]
    sections: list[bytes] = []

    for idx, y in enumerate(present):
        section = blocks[idx * 4096 : (idx + 1) * 4096]
        sections.append(_Y_HEAD + _Y_PACKED[y] + _BLOCKS_HEAD + section + _DUMMY_SECTIONS_PAYLOAD)

    return b"".join(
        [
            b"\x0a\x00\x00",  # compound tag
            _VERSION,
            _LEVEL_HEAD,
            _XPOS_HEAD,
            pack(">i", cx),
            _ZPOS_HEAD,
            pack(">i", cz),
            _SECTIONS_HEAD,
            b"\x0a",
            pack(">i", len(sections)),
            b"".join(sections),
            _DUMMY_CHUNK_PAYLOAD,
            _END,
        ]
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

        data = pack(">I", len(compressed_data) + len(compression_type)) + compression_type + compressed_data

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
