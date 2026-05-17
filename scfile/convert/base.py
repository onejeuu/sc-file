"""
Basic implementation of converting one format to another.
"""

from pathlib import Path
from typing import Optional, Type

from scfile import exceptions, types
from scfile.core import ContentType, FileDecoder, FileEncoder, UserOptions


def convert(
    decoder: Type[FileDecoder[ContentType]],
    encoder: Type[FileEncoder[ContentType]],
    source: types.PathLike,
    output: types.OutputLike = None,
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
    out_path = Path(output or src_path.parent)
    options = options or UserOptions()

    if not src_path.exists() or not src_path.is_file():
        raise exceptions.FileNotFound(str(src_path))

    if out_path.suffix == encoder.format.suffix:
        out_dir = out_path.parent
        out_name = out_path.name
    else:
        out_dir = out_path
        out_name = f"{src_path.stem}{encoder.format.suffix}"

    if not out_dir.exists():
        out_dir.mkdir(exist_ok=True, parents=True)

    output_path = out_dir / out_name

    match options.on_conflict:
        case "skip" if output_path.exists():
            return
        case "rename":
            output_path = ensure_unique_path(output_path)

    with decoder(src_path, options) as src:
        with src.convert_to(encoder=encoder) as out:
            out.save(path=output_path)


def ensure_unique_path(path: Path) -> Path:
    """Generates unique file path by appending counter if path exists."""

    filename, suffix = path.stem, path.suffix
    counter = 1

    while path.exists():
        path = path.parent / Path(f"{filename} ({counter}){suffix}")
        counter += 1

    return path
