"""
Basic implementation of converting one format to another.
"""

from pathlib import Path
from typing import Optional, Type

from scfile.core import FileDecoder, FileEncoder
from scfile.core.context.options import UserOptions
from scfile.core.types import Content, PathLike
from scfile.exceptions.file import FileNotFound


def convert(
    decoder: Type[FileDecoder[Content]],
    encoder: Type[FileEncoder[Content]],
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[UserOptions] = None,
) -> None:
    """Converts file between formats with basic validations."""

    src_path = Path(source)
    out_path = Path(output or source)
    options = options or UserOptions()

    if not src_path.exists() or not src_path.is_file():
        raise FileNotFound(src_path)

    if not out_path.parent.exists():
        out_path.parent.mkdir(exist_ok=True, parents=True)

    with decoder(file=src_path, options=options) as src:
        with src.convert_to(encoder=encoder) as out:
            output = out_path.with_suffix(out.suffix)

            if not options.overwrite:
                output = ensure_unique_path(path=output, suffix=out.suffix)

            out.save(path=output)


def ensure_unique_path(path: Path, suffix: str) -> Path:
    """Generates unique file path by appending counter if path exists."""

    filename = path.stem
    counter = 1

    while path.exists():
        path = path.parent / Path(f"{filename} ({counter}){suffix}")
        counter += 1

    return path
