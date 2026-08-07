"""
File conversion.
"""

from pathlib import Path
from typing import Optional

from scfile import exceptions, types
from scfile.core import BaseContent, Decoder, Encoder
from scfile.io import StructReader, StructWriter
from scfile.options import ConvertOptions
from scfile.registry import RESOLVER

from .types import Output, Status


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
    options: Optional[ConvertOptions] = None,
) -> Output:
    """Convert one file using explicitly selected handlers."""

    src_path = validate_sources(source)[0]
    output_path = destination(src_path, output, encoder.format.suffix)
    options = options or ConvertOptions()

    match options.conflict:
        case "skip" if output_path.exists():
            return Output(path=output_path, status=Status.SKIPPED)
        case "rename":
            output_path = ensure_unique_path(output_path)

    with decoder(src_path, options.handlers) as src:
        with src.convert_to(encoder=encoder) as out:
            out.save(path=output_path)

    return Output(path=output_path, status=Status.WRITTEN)


def auto(
    source: types.SourceLike,
    output: types.OutputLike = None,
    options: Optional[ConvertOptions] = None,
) -> list[Output]:
    """Convert one file using formats resolved from its extension."""

    src_path = Path(source)
    source_spec = RESOLVER.resolve(src_path)
    if source_spec is None or source_spec.decoder is None:
        raise exceptions.UnknownFormatError(str(src_path), src_path.suffix)

    options = options or ConvertOptions()
    targets = RESOLVER.targets(source_spec, options)
    if not targets:
        raise exceptions.ConversionError(
            f"No standalone output format available for '{source_spec.format}'.",
            location=str(src_path),
        )

    return [manual(source_spec.decoder, encoder, src_path, output, options) for encoder in targets.values()]


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
