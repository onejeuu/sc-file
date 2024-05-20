from pathlib import Path
from typing import NamedTuple, Optional, TypeVar

from scfile.file.base import FileDecoder, FileEncoder
from scfile.file.data import FileData
from scfile.io.binary import BinaryFileIO


OPENER = TypeVar("OPENER", bound=BinaryFileIO)
DATA = TypeVar("DATA", bound=FileData)


class Results(NamedTuple):
    converted: bytes
    expected: bytes


def extract(
    decoder: type[FileDecoder[OPENER, DATA]],
    encoder: type[FileEncoder[DATA]],
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
