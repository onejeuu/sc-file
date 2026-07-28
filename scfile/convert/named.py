"""
Named conversion functions.
"""

from functools import wraps
from pathlib import Path
from typing import Callable, Optional

from scfile.core import Options
from scfile.operations import convert
from scfile.registry import Decoder, Encoder
from scfile.types import PathLike


def converter(
    decoder: Decoder,
    encoder: Encoder,
) -> Callable:
    """Create a named conversion function for two handlers."""

    def decorator(func: Callable) -> Callable:
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

        return wrapper

    return decorator
