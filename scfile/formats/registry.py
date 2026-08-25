"""Format handler registry."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from scfile.core import Decoder, Encoder
from scfile.enums import FileFormat
from scfile.types import SourceLike


type DecoderType = type[Decoder[Any, Any]]
type EncoderType = type[Encoder[Any, Any]]


@dataclass(frozen=True, slots=True)
class Conversion:
    """One supported conversion path."""

    decoder: DecoderType
    encoder: EncoderType


class Registry:
    """Indexes built-in format handlers and conversion paths."""

    def __init__(
        self,
        decoders: Iterable[DecoderType],
        encoders: Iterable[EncoderType],
        aliases: Mapping[FileFormat, Iterable[str]],
    ) -> None:
        self.decoders = MappingProxyType({decoder.format: decoder for decoder in decoders})
        self.encoders = MappingProxyType({encoder.format: encoder for encoder in encoders})
        self.aliases = MappingProxyType(
            {format: frozenset(name.lower().lstrip(".") for name in names) for format, names in aliases.items()}
        )

        names = {
            name: self.decoders[format]
            for format, aliases in self.aliases.items()
            for name in aliases
            if format in self.decoders
        }
        names.update({format.suffix: decoder for format, decoder in self.decoders.items()})
        self._names = MappingProxyType(names)

        self.conversions = MappingProxyType(
            {
                (decoder.format, encoder.format): Conversion(decoder, encoder)
                for decoder in self.decoders.values()
                for encoder in self.encoders.values()
                if decoder.standalone and decoder.content_type is encoder.content_type
            }
        )

    def match(
        self,
        source: SourceLike,
    ) -> DecoderType | None:
        """Find an input handler for a file path."""

        path = Path(source)
        return self._names.get(path.name.lower()) or self._names.get(path.suffix.lower())

    def filters(
        self,
        *formats: FileFormat,
    ) -> frozenset[str]:
        """Return source filename filters."""

        selected = formats or tuple(self.decoders)
        return frozenset(
            name
            for format in selected
            for name in (format.suffix, *self.aliases.get(format, ()))
            if format in self.decoders
        )
