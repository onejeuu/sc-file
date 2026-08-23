import numpy as np

from scfile.io.ol import NULL, XOR, OlReader
from scfile.content.textures import CUBEMAP_FACE_COUNT


def test_sizes() -> None:
    values = np.array([16, 4], dtype="<u4")

    with OlReader(values.tobytes()) as reader:
        assert reader.sizes(2) == [16, 4]


def test_cubemap_sizes() -> None:
    values = np.arange(CUBEMAP_FACE_COUNT * 2, dtype="<u4")

    with OlReader(values.tobytes()) as reader:
        sizes = reader.cubemap_sizes(2)

    assert sizes == [list(range(6)), list(range(6, 12))]


def test_format() -> None:
    encoded = bytes(value ^ XOR for value in b"DXT1") + bytes([NULL]) * 12

    with OlReader(encoded) as reader:
        assert reader.format() == b"DXT1"
