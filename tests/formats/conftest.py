from typing import NamedTuple, Optional

from scfile import Options
from scfile.core import ContentType, FileDecoder, FileEncoder
from tests.conftest import ASSETS


class Compare(NamedTuple):
    source: bytes
    output: bytes


def extract(
    decoder: type[FileDecoder[ContentType]],
    encoder: type[FileEncoder[ContentType]],
    source: str,
    output: str,
    options: Optional[Options] = None,
) -> Compare:
    with decoder(ASSETS / "source" / source, options) as dec:
        converted = dec.convert(encoder)

    expected = (ASSETS / "output" / output).read_bytes()

    return Compare(converted, expected)
