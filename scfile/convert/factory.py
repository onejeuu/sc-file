"""
Decorator for registering named format converters.
"""

from collections import defaultdict
from copy import deepcopy
from functools import wraps
from typing import Callable, Optional, Type, TypeAlias

from scfile.core import ContentType, FileDecoder, FileEncoder, Options
from scfile.types import PathLike

from .convert import convert


ConverterMap: TypeAlias = dict[str, Callable]
ConverterRegistry: TypeAlias = dict[str, ConverterMap]

_REGISTRY: ConverterRegistry = defaultdict(dict)


def converters(src_format: str) -> ConverterMap:
    """Converters for source format."""
    return deepcopy(_REGISTRY.get(src_format.lower().lstrip("."), {}))


def registry() -> ConverterRegistry:
    """Copy of full converter registry."""
    return deepcopy(dict(_REGISTRY))


def converter(
    decoder: Type[FileDecoder[ContentType]],
    encoder: Type[FileEncoder[ContentType]],
) -> Callable:
    """Factory decorator for named conversion between two formats."""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(
            source: PathLike,
            output: Optional[PathLike] = None,
            options: Optional[Options] = None,
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
