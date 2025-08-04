"""
Internal factory decorator for convert functions.
"""

from functools import wraps
from typing import Callable, Optional, Type

from scfile.core import FileDecoder, FileEncoder, UserOptions
from scfile.core.types import Content
from scfile.types import PathLike

from .base import convert


def converter(
    decoder: Type[FileDecoder[Content]],
    encoder: Type[FileEncoder[Content]],
) -> Callable:
    """Factory decorator for base convert function with fixed decoder/encoder."""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(
            source: PathLike,
            output: Optional[PathLike] = None,
            options: Optional[UserOptions] = None,
        ):
            convert(
                decoder=decoder,
                encoder=encoder,
                source=source,
                output=output,
                options=options,
            )

        return wrapper

    return decorator
