from pathlib import Path
from typing import NamedTuple, Optional

from scfile.core import FileDecoder, FileEncoder
from scfile.core.types import Content


class Results(NamedTuple):
    converted: bytes
    expected: bytes


def extract(
    decoder: type[FileDecoder[Content]],
    encoder: type[FileEncoder[Content]],
    assets: Path,
    subdir: Optional[Path] = None,
    target: str = "output",
) -> Results:
    subdir = subdir or Path()

    source_path = assets / subdir / "input"
    output_path = assets / subdir / target

    with decoder(source_path) as dec:
        with dec.convert_to(encoder) as enc:
            converted = enc.getvalue()

    with open(output_path, "rb") as fp:
        expected = fp.read()

    return Results(converted, expected)
