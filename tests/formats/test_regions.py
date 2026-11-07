import struct

import pytest
import zstandard as zstd

from scfile.content import RegionContent
from scfile.formats.mca import McaEncoder
from scfile.formats.mdat import MdatDecoder
from scfile.options import Options


def _region(version: int) -> bytes:
    key_size = 8 if version == 7 else 16
    entry_size = 8 + key_size
    table_size = 1024 * entry_size
    sector = (table_size + 4095) // 4096

    terrain = bytes([42]) * 4096 + bytes(2048 * 4 + 256) + struct.pack(">i", 0)
    compressed = zstd.ZstdCompressor().compress(terrain)

    if version == 7:
        header = struct.pack(">i8s4i", 0, b"ABCDEFGH", 1, 0, len(terrain), len(compressed))
    else:
        header = struct.pack(">5i", 0, 1, 0, len(terrain), len(compressed))

    blob = header + compressed
    if version >= 6:
        objects = zstd.ZstdCompressor().compress(b"\x00")
        blob += struct.pack(">i", len(objects)) + objects

    count = (len(blob) + 4095) // 4096
    table = struct.pack(f">ii{key_size}s", sector, count, b"Z" * key_size)
    table += bytes(table_size - len(table))
    return table + bytes(sector * 4096 - table_size) + blob + bytes(count * 4096 - len(blob))


@pytest.mark.parametrize("version", [5, 6, 7])
@pytest.mark.parametrize("extended", [False, True])
def test_mdat_content_and_mca(version: int, extended: bool) -> None:
    with MdatDecoder(_region(version), options=Options(mdat_version=version, extended_chunk=extended)) as decoder:
        data = decoder.decode()
        assert isinstance(data, RegionContent)
        assert data is decoder.data
        assert len(data.chunks) == 1

        chunk = data.chunks[0]
        assert chunk.index == 0
        assert bytes(chunk.sections[0].blocks) == bytes([42]) * 4096
        assert len(chunk.biomes) == 256
        assert len(chunk.sections[0].metadata) == 2048
        assert (chunk.records is None) is (not extended)
        assert len(chunk.lighting) == 2048 * 3
        assert (chunk.objects is None) is (not extended or version == 5)
        if chunk.records is not None:
            assert chunk.records.count == 0
        if chunk.objects is not None:
            assert chunk.objects.count == 0

        with McaEncoder(data) as encoder:
            assert len(encoder.to_bytes()) >= 8192
