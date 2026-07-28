"""
Decorator for registering named format converters.
"""

from collections import defaultdict
from copy import deepcopy
from functools import wraps
from typing import Callable, Optional, Type, TypeAlias, TypeVar

from scfile.core import ContentType, FileDecoder, FileEncoder, Options
from scfile.types import PathLike

from .convert import convert


ConverterMap: TypeAlias = dict[str, Callable]
ConverterRegistry: TypeAlias = dict[str, ConverterMap]
DecoderMap: TypeAlias = dict[str, type[FileDecoder]]
EncoderMap: TypeAlias = dict[str, type[FileEncoder]]

Decoder: TypeAlias = Type[FileDecoder[ContentType]]
Encoder: TypeAlias = Type[FileEncoder[ContentType]]
Handler = TypeVar("Handler", bound=type[FileDecoder] | type[FileEncoder])

_REGISTRY: ConverterRegistry = defaultdict(dict)
_DECODERS: DecoderMap = {}
_ENCODERS: EncoderMap = {}


def decoders() -> DecoderMap:
    """Available format decoders."""
    return deepcopy({**_handlers(FileDecoder), **_DECODERS})


def encoders() -> EncoderMap:
    """Available format encoders."""
    return deepcopy({**_handlers(FileEncoder), **_ENCODERS})


def _handlers(base: Handler) -> dict[str, Handler]:
    from scfile import formats

    result = {}
    for name in formats.__all__:
        handler = getattr(formats, name)
        if isinstance(handler, type) and issubclass(handler, base):
            result[handler.format.lower()] = handler
    return result


def registry() -> ConverterRegistry:
    """Copy of full converter registry."""
    return deepcopy(dict(_REGISTRY))


def converters(
    src_format: str,
) -> ConverterMap:
    """Converters for source format."""
    return deepcopy(_REGISTRY.get(src_format.lower().lstrip("."), {}))


def _register(decoder: Decoder, encoder: Encoder, func: Callable) -> None:
    dec = decoder.format.lower()
    enc = encoder.format.lower()

    _DECODERS[dec] = decoder
    _ENCODERS[enc] = encoder
    _REGISTRY[dec][enc] = func


def _alias(source: str, target: str) -> None:
    _DECODERS[source] = _DECODERS[target]
    _REGISTRY[source] = _REGISTRY[target]


def converter(
    decoder: Decoder,
    encoder: Encoder,
    aliases: tuple[str, ...] = (),
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

        _register(
            decoder=decoder,
            encoder=encoder,
            func=wrapper,
        )

        for alias in aliases:
            _alias(alias, decoder.format.lower())

        return wrapper

    return decorator
