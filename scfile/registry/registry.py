"""
Format handlers registry.
"""

from collections.abc import Mapping
from copy import replace
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Optional, Self, TypeIs

from scfile.core import BaseContent, Decoder, Encoder, ModelContent, ModelEncoder
from scfile.enums import FileFormat
from scfile.exceptions import RegistryError
from scfile.options import Options
from scfile.structures.models import Feature
from scfile.types import FormatLike


# TODO: rework
def _is_decoder(handler: object) -> TypeIs[type[Decoder[Any, Any]]]:
    return isinstance(handler, type) and issubclass(handler, Decoder)


def _is_encoder(handler: object) -> TypeIs[type[Encoder[Any, Any]]]:
    return isinstance(handler, type) and issubclass(handler, Encoder)


def _format_name(value: str) -> str:
    return value.lower().lstrip(".")


@dataclass(frozen=True)
class FormatSpec:
    """Available handlers and content type for one file format."""

    format: FileFormat
    content: type[BaseContent]
    decoder: type[Decoder[Any, Any]] | None = None
    encoder: type[Encoder[Any, Any]] | None = None
    standalone: bool = True


class Registry:
    """Catalog of file formats and their handlers."""

    def __init__(
        self,
        *handlers: type[Decoder[Any, Any]] | type[Encoder[Any, Any]],
    ):
        self._formats: dict[FileFormat, FormatSpec] = {}
        self._aliases: dict[str, FileFormat] = {}
        self.register(*handlers)

    @property
    def formats(self) -> Mapping[FileFormat, FormatSpec]:
        """Registered formats."""

        return MappingProxyType(self._formats)

    @property
    def aliases(self) -> Mapping[str, FileFormat]:
        """Registered format aliases."""

        return MappingProxyType(self._aliases)

    @property
    def supported_formats(self) -> frozenset[FileFormat]:
        """Formats with a registered decoder."""

        return frozenset(fmt for fmt, spec in self._formats.items() if spec.decoder is not None)

    @property
    def supported_suffixes(self) -> frozenset[str]:
        """Input suffixes supported by registered decoders."""

        return frozenset(fmt.suffix for fmt in self.supported_formats)

    @property
    def supported_aliases(self) -> frozenset[str]:
        """Input names registered as format aliases."""

        return frozenset(self._aliases)

    @property
    def supported_inputs(self) -> frozenset[str]:
        """All input filename filters supported by registered decoders."""

        return self.filters_for()

    @property
    def model_formats(self) -> frozenset[FileFormat]:
        """Output formats backed by a model encoder."""

        return frozenset(
            fmt
            for fmt, spec in self._formats.items()
            if spec.encoder is not None and issubclass(spec.encoder, ModelEncoder)
        )

    def register(
        self,
        *handlers: type[Decoder[Any, Any]] | type[Encoder[Any, Any]],
    ) -> None:
        """Register format handlers."""

        for handler in handlers:
            self._register_handler(handler)

    def alias(
        self,
        target: FormatLike,
        *aliases: str,
    ) -> None:
        """Add alternative names for a registered format."""

        fmt = self.resolve(target)
        if fmt not in self._formats:
            raise RegistryError(f"Cannot alias unregistered format '{target}'.")

        for alias in aliases:
            self._aliases[_format_name(alias)] = fmt

    def aliases_for(
        self,
        target: FormatLike,
    ) -> frozenset[str]:
        """Return registered aliases for one format."""

        fmt = self.resolve(target)
        return frozenset(alias for alias, value in self._aliases.items() if value is fmt)

    def filters_for(
        self,
        *formats: FormatLike,
    ) -> frozenset[str]:
        """Return filename filters for registered source formats."""

        selected = formats or tuple(self.supported_formats)
        filters: set[str] = set()

        for value in selected:
            entry = self.get(value)
            if entry is None or entry.decoder is None:
                raise RegistryError(f"'{value}' is not a registered source format.")

            filters.add(entry.format.suffix)
            filters.update(self.aliases_for(entry.format))

        return frozenset(filters)

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
    ) -> type[Decoder[Any, Any]] | None:
        """Get decoder for format."""

        entry = self.get(value)
        return entry.decoder if entry else None

    def encoder(
        self,
        value: FormatLike,
    ) -> type[Encoder[Any, Any]] | None:
        """Get encoder for format."""

        entry = self.get(value)
        return entry.encoder if entry else None

    def model_supports(
        self,
        value: FormatLike,
        feature: Feature,
    ) -> bool:
        """Return whether a model output format supports a feature."""

        encoder = self.encoder(value)
        return bool(encoder and issubclass(encoder, ModelEncoder) and encoder.supports(feature))

    def decoders(self) -> dict[FileFormat, type[Decoder[Any, Any]]]:
        """Registered decoders."""

        return {fmt: entry.decoder for fmt, entry in self._formats.items() if entry.decoder is not None}

    def encoders(self) -> dict[FileFormat, type[Encoder[Any, Any]]]:
        """Registered encoders."""

        return {fmt: entry.encoder for fmt, entry in self._formats.items() if entry.encoder is not None}

    def targets(
        self,
        source: FormatLike,
    ) -> dict[FileFormat, type[Encoder[Any, Any]]]:
        """Encoders compatible with direct conversion from source format."""

        entry = self.get(source)
        if entry is None or entry.decoder is None or not entry.standalone:
            return {}

        return {
            fmt: target.encoder
            for fmt, target in self._formats.items()
            if target.encoder is not None and issubclass(entry.content, target.content)
        }

    def target(
        self,
        source: FormatLike,
        options: Optional[Options] = None,
    ) -> type[Encoder[Any, Any]] | None:
        """Select one default encoder compatible with a source format."""

        entry = self.get(source)
        available = self.targets(source)
        if entry is None or not available:
            return None

        options = options or Options()
        if issubclass(entry.content, ModelContent):
            return available.get(options.model_format or options.default_format)

        if len(available) == 1:
            return next(iter(available.values()))

        return None

    def copy(self) -> Self:
        """Create an independent registry copy."""

        copied = type(self)()
        copied._formats.update(self._formats)
        copied._aliases.update(self._aliases)
        return copied

    def _register_handler(self, handler: object) -> None:
        if _is_decoder(handler):
            self._set_decoder(handler)
            return

        if _is_encoder(handler):
            self._set_encoder(handler)
            return

        name = handler.__name__ if isinstance(handler, type) else type(handler).__name__
        raise RegistryError(f"{name} is not a file format handler.")

    def _set_decoder(self, decoder: type[Decoder[Any, Any]]) -> None:
        entry = self._entry(decoder.format, decoder.content_type)
        if entry.decoder is not None and entry.decoder is not decoder:
            raise RegistryError(f"{decoder.format} already has decoder {entry.decoder.__name__}.")

        self._formats[decoder.format] = replace(
            entry,
            decoder=decoder,
            standalone=decoder.standalone,
        )

    def _set_encoder(self, encoder: type[Encoder[Any, Any]]) -> None:
        entry = self._entry(encoder.format, encoder.content_type)
        if entry.encoder is not None and entry.encoder is not encoder:
            raise RegistryError(f"{encoder.format} already has encoder {entry.encoder.__name__}.")

        self._formats[encoder.format] = replace(
            entry,
            encoder=encoder,
        )

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
