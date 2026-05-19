from pathlib import Path
from typing import NamedTuple, Optional

import pytest

from scfile import UserOptions
from scfile.core import ContentType, FileDecoder, FileEncoder


class Compare(NamedTuple):
    source: bytes
    output: bytes


def extract(
    decoder: type[FileDecoder[ContentType]],
    encoder: type[FileEncoder[ContentType]],
    assets: Path,
    source: str,
    output: str,
    options: Optional[UserOptions] = None,
) -> Compare:
    with decoder(assets / "source" / source, options) as dec:
        converted = dec.convert(encoder)

    expected = (assets / "output" / output).read_bytes()

    return Compare(converted, expected)


@pytest.fixture
def assets() -> Path:
    return Path(__file__).parent / "assets"
