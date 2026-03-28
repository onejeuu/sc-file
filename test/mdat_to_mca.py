import argparse
import math
import os
import struct
import time
import zlib
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TypeAlias

import numpy as np

from scfile import formats
from scfile.core.context.content import RegionContent
from scfile.structures.region import RegionChunk


HEIGHT = 256
SECTION_SIZE = 16 * 16 * 16  # 4096
CURRENT_TIME = int(time.time())

RegionKey: TypeAlias = tuple[int, int]


def nbt(tag: int, name: str, payload: bytes) -> bytes:
    n = name.encode()
    return bytes([tag]) + struct.pack(">H", len(n)) + n + payload


def compound(name: str, *children: bytes) -> bytes:
    return nbt(0x0A, name, b"".join(children) + b"\x00")


def lst(name: str, typ: int, *items: bytes) -> bytes:
    return nbt(0x09, name, struct.pack(">bi", typ, len(items)) + b"".join(items))


def nbt_byte(name: str, v: int) -> bytes:
    return nbt(0x01, name, struct.pack(">b", v))


def nbt_int(name: str, v: int) -> bytes:
    return nbt(0x03, name, struct.pack(">i", v))


def nbt_long(name: str, v: int) -> bytes:
    return nbt(0x04, name, struct.pack(">q", v))


def nbt_ba(name: str, d: bytes) -> bytes:
    return nbt(0x07, name, struct.pack(">i", len(d)) + d)


def nbt_ia(name: str, a: tuple) -> bytes:
    return nbt(0x0B, name, struct.pack(f">i{len(a)}i", len(a), *a))


_MAPPING = {
    101: 1,
    198: 1,
    27: 1,
    28: 1,
    66: 1,
    158: 1,
    194: 35,
    178: 166,
}

_IDS_OLD = np.array(list(_MAPPING.keys()), dtype=np.uint8)
_IDS_NEW = np.array(list(_MAPPING.values()), dtype=np.uint8)
_LOOKUP = np.arange(256, dtype=np.uint8)
_LOOKUP[_IDS_OLD] = _IDS_NEW


def terrain_to_sections_raw(data: bytes) -> dict[int, bytes]:
    data = data.ljust(0x10000, b"\x00")
    return {y: data[y * SECTION_SIZE : y * SECTION_SIZE + SECTION_SIZE] for y in range(16)}


def terrain_to_sections(data: bytes) -> dict[int, bytes]:
    data = data.ljust(0x10000, b"\x00")
    arr = np.frombuffer(data, dtype=np.uint8)
    data = _LOOKUP[arr].tobytes()

    return {y: data[y * SECTION_SIZE : y * SECTION_SIZE + SECTION_SIZE] for y in range(16)}


_VERSION = nbt_int("DataVersion", 1343)

_DUMMY_PAYLOAD = (
    nbt_long("LastUpdate", CURRENT_TIME)
    + nbt_byte("TerrainPopulated", 1)
    + nbt_byte("LightPopulated", 1)
    + nbt_byte("V", 1)
    + nbt_long("InhabitedTime", 6000)
    + nbt_ia("HeightMap", tuple([6] * HEIGHT))
    + nbt_ba("Biomes", b"\x01" * HEIGHT)
    + lst("Entities", 0x0A)
    + lst("TileEntities", 0x0A)
    + lst("TileTicks", 0x0A)
)

_DUMMY_SECTIONS_PAYLOAD = (
    nbt_ba("Data", bytes(2048))
    + nbt_ba("BlockLight", bytes(2048))
    + nbt_ba("SkyLight", b"\xff" * 2048)
    + nbt_ba("Add", bytes(2048))
    + b"\x00"
)


def section_payload(y: int, blocks: bytes) -> bytes:
    return nbt_byte("Y", y) + nbt_ba("Blocks", blocks) + _DUMMY_SECTIONS_PAYLOAD


def chunk_nbt(cx: int, cz: int, chunk: RegionChunk) -> bytes:
    sections = terrain_to_sections(chunk.blocks)

    return compound(
        "",
        _VERSION,
        compound(
            "Level",
            nbt_int("xPos", cx),
            nbt_int("zPos", cz),
            lst("Sections", 0x0A, *[section_payload(y, blocks) for y, blocks in sections.items()]),
            _DUMMY_PAYLOAD,
        ),
    )


def build_mca(out: Path, region: RegionContent, rx: int = 0, rz: int = 0) -> None:
    chunks: list[tuple[int, int, bytes]] = []

    for chunk in region.chunks:
        index = chunk.index

        lx = index % 32
        lz = index // 32
        cx = rx * 32 + lx
        cz = rz * 32 + lz

        data = zlib.compress(chunk_nbt(cx, cz, chunk))

        chunks.append((lx, lz, data))

    # location & timestamp
    loc = np.zeros(SECTION_SIZE, dtype=np.uint8)
    ts = np.zeros(SECTION_SIZE, dtype=np.uint8)

    off = 2
    offsets: list[tuple[int, int]] = []

    for lx, lz, data in chunks:
        sc = math.ceil((len(data) + 5) / SECTION_SIZE)  # section size
        i4 = (lx + lz * 32) * 4  # location table entry

        # pack offsets
        loc[i4] = (off >> 16) & 0xFF
        loc[i4 + 1] = (off >> 8) & 0xFF
        loc[i4 + 2] = off & 0xFF
        loc[i4 + 3] = sc

        # pack times
        ts_bytes = struct.pack(">I", CURRENT_TIME)
        ts[i4 : i4 + 4] = np.frombuffer(ts_bytes, dtype=np.uint8)

        offsets.append((off, sc))
        off += sc

    with open(out, "wb") as fp:
        fp.write(loc.tobytes())
        fp.write(ts.tobytes())

        for (chunk_off, sc), (lx, lz, data) in zip(offsets, chunks):
            fp.seek(chunk_off * SECTION_SIZE)
            blob = struct.pack(">I", len(data) + 1) + b"\x02" + data
            padded = blob + b"\x00" * (sc * SECTION_SIZE - len(blob))
            fp.write(padded)


def merge(item: tuple[RegionKey, list[Path]], output: Path) -> None:
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
    build_mca(output / filename, region=merged, rx=rx, rz=rz)
    print(f"{filename}: {len(merged.chunks)} chunks")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert MDAT to MCA (1.12.2) format")
    parser.add_argument("source", type=Path, help="Source directory with MDAT files")
    parser.add_argument("output", type=Path, help="Output directory for MCA files")
    parser.add_argument("-w", "--workers", type=int, default=None, help="Number of worker threads (default: CPU count)")

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

    max_workers = (args.workers or os.cpu_count() or 4) * 2
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(lambda item: merge(item, output), regions.items())

    print("Done.")


if __name__ == "__main__":
    main()
