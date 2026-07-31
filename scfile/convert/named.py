"""
Named conversion functions.
"""

from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, Optional, cast

from scfile.operations import convert
from scfile.options import Options
from scfile.registry import Decoder, Encoder
from scfile.types import PathLike


type Converter = Callable[[PathLike, Optional[PathLike], Optional[Options]], Path]


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
            options: Optional[Options] = None,
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
