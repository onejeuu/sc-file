"""File conversion."""

from pathlib import Path
from typing import Optional

from scfile import exceptions, types
from scfile.core import BaseContent, Decoder, Encoder
from scfile.io import StructReader, StructWriter
from scfile.options import Options
from scfile.registry import REGISTRY, RESOLVER

from . import paths


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

    options = options or Options()

    src = paths.source(source)
    out = paths.output(src, output, encoder.suffix(), options)

    if out is None:
        return

    with decoder(src, options) as dec:
        content = dec.decode()

    with paths.stage(out) as tmp:
        with encoder(content, options, output=tmp) as enc:
            enc.encode()

    return out


def auto(
    source: types.SourceLike,
    output: types.OutputLike = None,
    options: Optional[Options] = None,
) -> types.ResultPath:
    """Convert one file using formats resolved from its extension.

    Returns ``None`` when an existing output is skipped.
    """

    options = options or Options()

    src = Path(source)
    spec = RESOLVER.resolve(src)

    if spec is None or spec.decoder is None:
        raise exceptions.UnknownFormatError(str(src), src.suffix)

    encoder = REGISTRY.target(spec.format, options)
    if encoder is None:
        raise exceptions.ConversionError(
            f"No standalone output format available for '{spec.format}'.",
            location=str(src),
        )

    return manual(spec.decoder, encoder, src, output, options)
