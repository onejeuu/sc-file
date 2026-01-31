from pathlib import Path
from typing import NamedTuple

from scfile.core import FileDecoder, FileEncoder
from scfile.core.types import Content


class Results(NamedTuple):
    converted: bytes
    expected: bytes


def extract(
    decoder: type[FileDecoder[Content]],
    encoder: type[FileEncoder[Content]],
    assets: Path,
    source: str = "input",
    output: str = "output",
) -> Results:
    with decoder(assets / source) as dec:
        with dec.convert_to(encoder) as enc:
            converted = enc.getvalue()

    with open(assets / output, "rb") as fp:
        expected = fp.read()

    return Results(converted, expected)
