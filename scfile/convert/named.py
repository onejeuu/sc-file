"""Named conversion decorator."""

from collections.abc import Callable
from functools import wraps
from typing import Any, Optional, cast

from scfile.content import BaseContent
from scfile.core import Decoder, Encoder
from scfile.io import StructReader, StructWriter
from scfile.options import Options
from scfile.types import OutputLike, ResultPath, SourceLike

from .files import manual


type Converter = Callable[[SourceLike, OutputLike, Optional[Options]], ResultPath]


def converter[
    ContentType: BaseContent,
    ReaderType: StructReader,
    WriterType: StructWriter,
](
    decoder: type[Decoder[ContentType, ReaderType]],
    encoder: type[Encoder[ContentType, WriterType]],
) -> Callable[[Callable[..., Any]], Converter]:
    """Create a named conversion function for selected handlers."""

    def decorator(func: Callable[..., Any]) -> Converter:
        @wraps(func)
        def wrapper(
            source: SourceLike,
            output: OutputLike = None,
            options: Optional[Options] = None,
        ) -> ResultPath:
            return manual(
                decoder=decoder,
                encoder=encoder,
                source=source,
                output=output,
                options=options,
            )

        return cast(Converter, wrapper)

    return decorator
