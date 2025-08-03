"""
Basic implementation of converting one format to another.
"""

from pathlib import Path
from typing import Optional, Type

from scfile import exceptions
from scfile.core import FileDecoder, FileEncoder, UserOptions
from scfile.core.types import Content
from scfile.types import OutputDir, PathLike


def convert(
    decoder: Type[FileDecoder[Content]],
    encoder: Type[FileEncoder[Content]],
    source: PathLike,
    output: OutputDir = None,
    options: Optional[UserOptions] = None,
) -> None:
    """
    Converts file between formats with basic validations.

    Arguments:
        decoder: Input file decoder class.
        encoder: Output file encoder class.
        source: Path to input file.
        output (optional): Path to output directory. Defaults: `Same directory as source`.
        options (optional): User settings. Default: `None`.

    Example:
        `convert(McsaDecoder, ObjEncoder, "model.mcsb", "path/to/output")`
    """

    src_path = Path(source)
    out_dir = Path(output or src_path.parent)
    options = options or UserOptions()

    if not src_path.exists() or not src_path.is_file():
        raise exceptions.FileNotFound(src_path)

    if not out_dir.exists():
        out_dir.mkdir(exist_ok=True, parents=True)

    with decoder(file=src_path, options=options) as src:
        with src.convert_to(encoder=encoder) as out:
            output = out_dir / f"{src_path.stem}{out.suffix}"

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
