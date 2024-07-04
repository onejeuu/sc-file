from pathlib import Path
from typing import Optional

from scfile import consts
from scfile import exceptions as exc
from scfile.file.base import FileDecoder, FileEncoder
from scfile.file.base.decoder import DATA, OPENER
from scfile.utils.types import PathLike


def is_supported(source: PathLike) -> bool:
    return Path(source).suffix.lstrip(".") in consts.SUPPORTED_SUFFIXES


def convert(
    source: PathLike,
    output: Optional[PathLike],
    decoder: type[FileDecoder[OPENER, DATA]],
    encoder: type[FileEncoder[DATA]],
    overwrite: bool = True,
):
    source = Path(source)
    output = Path(output or source.parent)

    new_suffix = encoder.suffix()
    new_source = source.with_suffix(f".{new_suffix}")

    # Check that file exists
    if not source.exists() or not source.is_file():
        raise exc.FileNotFound(source)

    # Full destination path
    destination = output / new_source.name

    # If overwrite is disabled
    # Validate that file with that name doesn't exist
    if not overwrite:
        counter = 1
        while Path(destination).exists():
            destination = output / Path(f"{new_source.stem} ({counter}).{new_suffix}")
            counter += 1

    # Create output directory
    destination.parent.mkdir(parents=True, exist_ok=True)

    # Convert and save file to destination path
    with decoder(source) as dec:
        dec.convert_to(encoder).save(destination)
