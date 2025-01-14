from pathlib import Path
from typing import NamedTuple, Optional

from scfile.core import FileDecoder, FileEncoder
from scfile.core.decoder import Opener
from scfile.core.types import Context, Options


class Results(NamedTuple):
    converted: bytes
    expected: bytes


def extract(
    decoder: type[FileDecoder[Opener, Context, Options]],
    encoder: type[FileEncoder[Context, Options]],
    assets: Path,
    subdir: Optional[Path] = None,
    output_filename: str = "output",
) -> Results:
    subdir = subdir or Path()

    source_path = assets / subdir / "input"
    output_path = assets / subdir / output_filename

    with decoder(source_path) as dec:
        with dec.convert_to(encoder) as enc:
            converted = enc.content

    with open(output_path, "rb") as fp:
        expected = fp.read()

    return Results(converted, expected)
