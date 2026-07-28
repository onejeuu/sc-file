"""
Basic implementation of converting one format to another.
"""

from pathlib import Path
from typing import Optional, Type

from scfile import exceptions, types
from scfile.core import ContentType, FileDecoder, FileEncoder, Options


def convert(
    decoder: Type[FileDecoder[ContentType]],
    encoder: Type[FileEncoder[ContentType]],
    source: types.PathLike,
    output: types.OutputLike = None,
    options: Optional[Options] = None,
) -> None:
    """
    Convert one file between formats.

    Args:
        decoder: Decoder class for source format.
        encoder: Encoder class for output format.
        source: Path to source file.
        output (optional): Path to output file or directory. Defaults to source directory.
        options (optional): Shared handlers options.

    Raises:
        FileNotFound: Source file does not exist.

    Example:
        - ``convert(McsaDecoder, ObjEncoder, "model.mcsb", "model.obj")``
        - ``convert(McsaDecoder, ObjEncoder, "model.mcsb", "path/to/output/dir")``
    """

    src_path = validate_sources(source)[0]
    output_path = destination(src_path, output, encoder.format.suffix)
    options = options or Options()

    match options.on_conflict:
        case "skip" if output_path.exists():
            return
        case "rename":
            output_path = ensure_unique_path(output_path)

    with decoder(src_path, options) as src:
        with src.convert_to(encoder=encoder) as out:
            out.save(path=output_path)


def validate_sources(*sources: types.PathLike) -> list[Path]:
    """Resolve source paths and require regular files."""

    paths = [Path(source) for source in sources]
    for path in paths:
        if not path.exists() or not path.is_file():
            raise exceptions.FileNotFound(str(path))

    return paths


def destination(
    source: Path,
    output: types.OutputLike,
    suffix: str,
) -> Path:
    """Resolve output file path and create its directory."""

    path = Path(output or source.parent)
    if path.suffix == suffix:
        result = path
    else:
        result = path / f"{source.stem}{suffix}"

    result.parent.mkdir(exist_ok=True, parents=True)
    return result


def ensure_unique_path(path: Path) -> Path:
    """Append a counter to path if a file already exists."""

    filename, suffix = path.stem, path.suffix
    counter = 1

    while path.exists():
        path = path.parent / Path(f"{filename} ({counter}){suffix}")
        counter += 1

    return path
