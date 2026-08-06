from io import BytesIO

import pytest

from scfile.exceptions import Ms3dCapacityError
from scfile.io.ms3d import STRING_SIZE, Ms3dWriter


def test_fixed_string() -> None:
    with Ms3dWriter(BytesIO()) as writer:
        writer.fixed_string("bone")

        assert writer.to_bytes() == b"bone".ljust(STRING_SIZE, b"\x00")


def test_string_limit() -> None:
    writer = Ms3dWriter(BytesIO())

    with pytest.raises(Ms3dCapacityError):
        writer.fixed_string("x" * (STRING_SIZE + 1))

    writer.close()


def test_count() -> None:
    with Ms3dWriter(BytesIO()) as writer:
        writer.count("vertices", 2, 512)

        assert writer.to_bytes() == b"\x02\x00"
