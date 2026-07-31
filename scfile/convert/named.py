"""
Named conversion functions.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any, Optional, cast

from scfile.options import ConvertOptions
from scfile.registry import Decoder, Encoder
from scfile.types import PathLike

from .files import Result, manual


type Converter = Callable[[PathLike, Optional[PathLike], Optional[ConvertOptions]], Result]


def converter(
    decoder: Decoder,
    encoder: Encoder,
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
