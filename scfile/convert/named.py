"""
Named conversion functions.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any, Optional, cast

from scfile.core import BaseContent, Decoder, Encoder
from scfile.io import StructReader, StructWriter
from scfile.options import ConvertOptions
from scfile.types import PathLike

from .files import manual
from .types import Result


type Converter = Callable[[PathLike, Optional[PathLike], Optional[ConvertOptions]], Result]


def converter[
    ContentType: BaseContent,
    ReaderType: StructReader,
    WriterType: StructWriter,
](
    decoder: type[Decoder[ContentType, ReaderType]],
    encoder: type[Encoder[ContentType, WriterType]],
) -> Callable[[Callable[..., Any]], Converter]:
    """Create a named conversion function for two handlers."""

    def decorator(func: Callable[..., Any]) -> Converter:
        @wraps(func)
        def wrapper(
            source: PathLike,
            output: Optional[PathLike] = None,
            options: Optional[ConvertOptions] = None,
        ) -> Result:
            return manual(
                decoder=decoder,
                encoder=encoder,
                source=source,
                output=output,
                options=options,
            )

        return cast(Converter, wrapper)

    return decorator
