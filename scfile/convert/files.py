"""File conversion."""

from pathlib import Path
from typing import Optional

from scfile import exceptions, types
from scfile.content import BaseContent
from scfile.core import Decoder, Encoder
from scfile.formats import registry
from scfile.io import StructReader, StructWriter
from scfile.options import Options

from . import paths


def format(
    source: types.SourceLike,
) -> str:
    """Detect input file format."""

    if decoder := registry.match(source):
        return str(decoder.format)

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
    decoder = registry.match(src)

    if decoder is None:
        raise exceptions.UnknownFormatError(str(src), src.suffix)

    target = options.targets[decoder.content_type]
    conversion = registry.conversions.get((decoder.format, target))
    if conversion is None:
        raise exceptions.ConversionError(
            f"Cannot convert '{decoder.format}' to '{target}'.",
            location=str(src),
        )

    return manual(conversion.decoder, conversion.encoder, src, output, options)
