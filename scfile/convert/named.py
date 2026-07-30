"""
Named conversion functions.
"""

from functools import wraps
from pathlib import Path
from typing import Any, Callable, cast

from scfile.core import Options
from scfile.operations import convert
from scfile.registry import Decoder, Encoder
from scfile.types import PathLike


Converter = Callable[[PathLike, PathLike | None, Options | None], Path]


def converter(
    decoder: Decoder,
    encoder: Encoder,
) -> Callable[[Callable[..., Any]], Converter]:
    """Create a named conversion function for two handlers."""

    def decorator(func: Callable[..., Any]) -> Converter:
        @wraps(func)
        def wrapper(
            source: PathLike,
            output: PathLike | None = None,
            options: Options | None = None,
        ) -> Path:
            return convert(
                decoder=decoder,
                encoder=encoder,
                source=source,
                output=output,
                options=options,
            )

        return cast(Converter, wrapper)

    return decorator
