"""
File conversion.
"""

from pathlib import Path
from typing import Optional

from scfile import exceptions, types
from scfile.core import BaseContent, Decoder, Encoder
from scfile.io import StructReader, StructWriter
from scfile.options import Options
from scfile.registry import REGISTRY, RESOLVER


def format(
    source: types.SourceLike,
) -> str:
    """Detect input file format."""

    if spec := RESOLVER.resolve(source):
        return str(spec.format)

    return Path(source).suffix.lower().lstrip(".")


def manual[
    ContentType: BaseContent,
    ReaderType: StructReader,
    WriterType: StructWriter,
](
    decoder: type[Decoder[ContentType, ReaderType]],
    encoder: type[Encoder[ContentType, WriterType]],
    source: types.SourceLike,
    output: types.OutputLike = None,
    options: Optional[Options] = None,
) -> types.ResultPath:
    """Convert one file using explicitly selected handlers.

    Returns ``None`` when an existing output is skipped.
    """

    src_path = validate_sources(source)[0]
    options = options or Options()
    output_path = resolve_output(src_path, output, encoder.format.suffix, options)
    if output_path is None:
        return None

    with decoder(src_path, options) as src:
        with src.convert_to(encoder=encoder) as out:
            out.save(path=output_path)

    return output_path


def auto(
    source: types.SourceLike,
    output: types.OutputLike = None,
    options: Optional[Options] = None,
) -> types.ResultPath:
    """Convert one file using formats resolved from its extension.

    Returns ``None`` when an existing output is skipped.
    """

    src_path = Path(source)
    source_spec = RESOLVER.resolve(src_path)
    if source_spec is None or source_spec.decoder is None:
        raise exceptions.UnknownFormatError(str(src_path), src_path.suffix)

    options = options or Options()
    encoder = REGISTRY.target(source_spec.format, options)
    if encoder is None:
        raise exceptions.ConversionError(
            f"No standalone output format available for '{source_spec.format}'.",
            location=str(src_path),
        )

    return manual(source_spec.decoder, encoder, src_path, output, options)


def validate_sources(
    *sources: types.SourceLike,
) -> list[Path]:
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


def resolve_output(
    source: Path,
    output: types.OutputLike,
    suffix: str,
    options: Options,
) -> types.ResultPath:
    """Resolve one output path and apply its conflict policy."""

    path = destination(source, output, suffix)
    match options.on_conflict:
        case "skip" if path.exists():
            return None
        case "rename":
            return ensure_unique_path(path)
        case _:
            return path


def ensure_unique_path(
    path: Path,
) -> Path:
    """Append a counter to path if a file already exists."""

    filename, suffix = path.stem, path.suffix
    counter = 1

    while path.exists():
        path = path.parent / Path(f"{filename} ({counter}){suffix}")
        counter += 1

    return path
