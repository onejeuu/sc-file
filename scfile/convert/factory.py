"""
Internal factory decorator for convert functions.
"""

from collections import defaultdict
from copy import deepcopy
from functools import wraps
from typing import Callable, Optional, Type, TypeAlias

from scfile.core import FileDecoder, FileEncoder, UserOptions
from scfile.core.types import Content
from scfile.types import PathLike

from .base import convert


ConverterMap: TypeAlias = dict[str, Callable]
ConverterRegistry: TypeAlias = dict[str, ConverterMap]

_REGISTRY: ConverterRegistry = defaultdict(dict)


def converters(src_format: str) -> ConverterMap:
    return deepcopy(_REGISTRY.get(src_format.lower().lstrip("."), {}))


def registry() -> ConverterRegistry:
    return deepcopy(_REGISTRY)


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

        _REGISTRY[decoder.format.lower()][encoder.format.lower()] = wrapper

        return wrapper

    return decorator
