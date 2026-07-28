"""
Format handlers registry.
"""

from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Any, Mapping, Self, TypeAlias

from scfile.core import BaseContent, FileDecoder, FileEncoder
from scfile.enums import FileFormat
from scfile.exceptions import RegistryError


Decoder: TypeAlias = type[FileDecoder[Any, Any]]
Encoder: TypeAlias = type[FileEncoder[Any, Any]]
Handler: TypeAlias = Decoder | Encoder
FormatLike: TypeAlias = str | FileFormat


def _format_name(value: str) -> str:
    return value.lower().lstrip(".")


@dataclass(frozen=True)
class FormatSpec:
    """Available handlers and content type for one file format."""

    format: FileFormat
    content: type[BaseContent]
    decoder: Decoder | None = None
    encoder: Encoder | None = None
    convertible: bool = True


class Registry:
    """Catalog of file formats and their handlers."""

    def __init__(
        self,
        *handlers: Handler,
    ):
        self._formats: dict[FileFormat, FormatSpec] = {}
        self._aliases: dict[str, FileFormat] = {}
        self.register(*handlers)

    @property
    def formats(self) -> Mapping[FileFormat, FormatSpec]:
        """Registered formats."""

        return MappingProxyType(self._formats)

    def register(
        self,
        *handlers: Handler,
    ) -> None:
        """Register format handlers."""

        for handler in handlers:
            self._register_handler(handler)

    def alias(
        self,
        alias: str,
        target: FormatLike,
    ) -> None:
        """Add another name for a registered format."""

        self._aliases[_format_name(alias)] = self.resolve(target)

    def resolve(
        self,
        value: FormatLike,
    ) -> FileFormat:
        """Resolve format enum, value, suffix or alias."""

        if isinstance(value, FileFormat):
            return value

        name = _format_name(value)
        if name in self._aliases:
            return self._aliases[name]

        try:
            return FileFormat(name)

        except ValueError as error:
            raise RegistryError(f"Unknown format '{value}'.") from error

    def get(
        self,
        value: FormatLike,
    ) -> FormatSpec | None:
        """Get format entry if registered."""

        try:
            fmt = self.resolve(value)

        except RegistryError:
            return None

        return self._formats.get(fmt)

    def decoder(
        self,
        value: FormatLike,
    ) -> Decoder | None:
        """Get decoder for format."""

        entry = self.get(value)
        return entry.decoder if entry else None

    def encoder(
        self,
        value: FormatLike,
    ) -> Encoder | None:
        """Get encoder for format."""

        entry = self.get(value)
        return entry.encoder if entry else None

    def decoders(self) -> dict[FileFormat, Decoder]:
        """Registered decoders."""

        return {fmt: entry.decoder for fmt, entry in self._formats.items() if entry.decoder is not None}

    def encoders(self) -> dict[FileFormat, Encoder]:
        """Registered encoders."""

        return {fmt: entry.encoder for fmt, entry in self._formats.items() if entry.encoder is not None}

    def targets(
        self,
        source: FormatLike,
    ) -> dict[FileFormat, Encoder]:
        """Encoders compatible with direct conversion from source format."""

        entry = self.get(source)
        if entry is None or entry.decoder is None or not entry.convertible:
            return {}

        return {
            fmt: target.encoder
            for fmt, target in self._formats.items()
            if target.encoder is not None and issubclass(entry.content, target.content)
        }

    def copy(self) -> Self:
        """Create an independent registry copy."""

        copied = type(self)()
        copied._formats.update(self._formats)
        copied._aliases.update(self._aliases)
        return copied

    def _register_handler(self, handler: Handler) -> None:
        if issubclass(handler, FileDecoder):
            self._set_decoder(handler)
            return

        self._set_encoder(handler)

    def _set_decoder(self, decoder: Decoder) -> None:
        entry = self._entry(decoder.format, decoder.content_factory)
        if entry.decoder is not None and entry.decoder is not decoder:
            raise RegistryError(f"{decoder.format} already has decoder {entry.decoder.__name__}.")

        self._formats[decoder.format] = replace(
            entry,
            decoder=decoder,
            convertible=decoder.convertible,
        )

    def _set_encoder(self, encoder: Encoder) -> None:
        entry = self._entry(encoder.format, encoder.content_type)
        if entry.encoder is not None and entry.encoder is not encoder:
            raise RegistryError(f"{encoder.format} already has encoder {entry.encoder.__name__}.")

        self._formats[encoder.format] = replace(entry, encoder=encoder)

    def _entry(
        self,
        fmt: FileFormat,
        content_type: type[BaseContent],
    ) -> FormatSpec:
        entry = self._formats.get(fmt)
        if entry is None:
            return FormatSpec(fmt, content_type)

        if entry.content is not content_type:
            raise RegistryError(
                f"{fmt} handlers use different content types: {entry.content.__name__} and {content_type.__name__}."
            )

        return entry
