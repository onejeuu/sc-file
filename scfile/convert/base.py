"""
Basic implementation of converting one format to another.
"""

from pathlib import Path
from typing import Optional, Type

from scfile import exceptions as exc
from scfile.consts import SUPPORTED_SUFFIXES
from scfile.core import FileDecoder, FileEncoder
from scfile.core.types import Content, Options, PathLike


def is_supported(source: PathLike) -> bool:
    return Path(source).suffix in SUPPORTED_SUFFIXES


def convert(
    decoder: Type[FileDecoder[Content, Options]],
    encoder: Type[FileEncoder[Content, Options]],
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
    overwrite: bool = True,
):
    """Convert file"""
    src_path = Path(source)
    out_path = Path(output or source)

    if not src_path.exists() or not src_path.is_file():
        raise exc.FileNotFound(src_path)

    if not out_path.parent.exists():
        out_path.parent.mkdir(exist_ok=True, parents=True)

    with decoder(file=src_path, options=options) as src:
        with src.convert_to(encoder=encoder) as out:
            output = out_path.with_suffix(out.suffix)

            if not overwrite:
                output = ensure_unique_path(path=output, suffix=out.suffix)

            out.save(path=output)


def ensure_unique_path(path: Path, suffix: str) -> Path:
    filename = path.stem
    counter = 1

    while path.exists():
        path = path.parent / Path(f"{filename} ({counter}){suffix}")
        counter += 1

    return path
