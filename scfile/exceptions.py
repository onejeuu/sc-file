"""Library exceptions."""

from typing import ClassVar

from scfile.enums import HandlerState


class ScFileException(Exception):
    """Base exception for scfile library."""

    unsupported: ClassVar[bool] = False
    """Whether the condition is intentionally unsupported."""

    def __init__(
        self,
        message: str,
        *,
        location: str | None = None,
        offset: int | None = None,
    ) -> None:
        super().__init__(message)
        self.location = location
        self.offset = offset

    def __str__(self) -> str:
        message = super().__str__()
        if self.offset is None:
            return message
        return f"{message} (offset: {self.offset})."


class HandlerStateError(ScFileException):
    """Raised when an operation is unavailable in the current handler state."""

    def __init__(
        self,
        operation: str,
        state: HandlerState,
        *,
        closed: bool = False,
        location: str | None = None,
    ) -> None:
        condition = "handler is closed" if closed else f"handler is in '{state}' state"
        super().__init__(
            f"Cannot {operation}: {condition}.",
            location=location,
        )
        self.operation = operation
        self.state = state
        self.closed = closed


class FileError(ScFileException):
    """Base exception for source file access and recognition."""

    ...


class FileNotFound(FileError):
    """Raised when a source file does not exist."""

    def __init__(
        self,
        location: str,
    ) -> None:
        super().__init__("File not found.", location=location)


class EmptyFileError(FileError):
    """Raised when a source file is empty."""

    def __init__(
        self,
        location: str,
    ) -> None:
        super().__init__("File is empty.", location=location)


class UnknownFormatError(FileError):
    """Raised when a source file format cannot be identified."""

    def __init__(
        self,
        location: str,
        format: str,
    ) -> None:
        super().__init__(f"Unknown format '{format}'.", location=location)
        self.format = format


class DecodingError(ScFileException):
    """Base exception raised while decoding a file."""

    ...


class ModelVersionError(DecodingError):
    """Raised when a model version is not supported."""

    unsupported = True

    def __init__(
        self,
        version: float,
        *,
        location: str | None = None,
        offset: int | None = None,
    ) -> None:
        super().__init__(
            f"Unsupported model version: {version}.",
            location=location,
            offset=offset,
        )
        self.version = version


class TextureFormatError(DecodingError):
    """Raised when a texture format is not supported."""

    unsupported = True

    def __init__(
        self,
        format: bytes,
        *,
        location: str | None = None,
        offset: int | None = None,
    ) -> None:
        super().__init__(
            f"Unsupported texture format: {format!r}.",
            location=location,
            offset=offset,
        )
        self.format = format


class TextureKindError(DecodingError):
    """Raised when a texture kind is not supported."""

    unsupported = True

    def __init__(
        self,
        kind: int,
        *,
        location: str | None = None,
        offset: int | None = None,
    ) -> None:
        super().__init__(
            f"Unsupported texture kind: {kind}.",
            location=location,
            offset=offset,
        )
        self.kind = kind


class SignatureMismatchError(DecodingError):
    """Raised when a file signature differs from the expected value."""

    def __init__(
        self,
        actual: bytes,
        expected: bytes,
        *,
        location: str | None = None,
        offset: int | None = None,
    ) -> None:
        super().__init__(
            f"Signature mismatch: {actual.hex().upper()} != {expected.hex().upper()}.",
            location=location,
            offset=offset,
        )
        self.actual = actual
        self.expected = expected


class BinaryStructureError(DecodingError):
    """Raised when binary data does not match the expected structure."""

    hint: ClassVar[str] = "Input file appears to be corrupted or invalid."

    def __init__(
        self,
        *,
        location: str | None = None,
        offset: int | None = None,
    ) -> None:
        super().__init__(self._message(), location=location, offset=offset)

    def _message(self) -> str:
        return "Unexpected binary structure."


class SafetyLimitError(BinaryStructureError):
    """Raised when a decoded value exceeds a safety limit."""

    def __init__(
        self,
        subject: str,
        count: int,
        maximum: int,
        *,
        location: str | None = None,
        offset: int | None = None,
    ) -> None:
        self.subject = subject
        self.count = count
        self.maximum = maximum
        super().__init__(location=location, offset=offset)

    def _message(self) -> str:
        return f"Safety limit exceeded: {self.count:,} {self.subject} (max: {self.maximum:,})."


class EncodingError(ScFileException):
    """Base exception raised while encoding a file."""

    ...


class ConversionError(ScFileException):
    """Raised when requested format conversion is unavailable."""

    ...


class AnimationError(ScFileException):
    """Raised when animation cannot be applied to a model."""

    ...


class RegistryError(ScFileException):
    """Raised when registry lookup or registration fails."""

    ...


class RegionError(ScFileException):
    """Base exception for region operations."""

    ...


class MergeInterrupted(RegionError):
    """Raised when region merge is interrupted by user."""

    def __init__(self) -> None:
        super().__init__("Merge interrupted.")
