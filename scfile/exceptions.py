"""
Library exceptions and diagnostic context.
"""

from typing import ClassVar, Optional


class ScFileException(Exception):
    """Base exception for scfile library."""

    unsupported: ClassVar[bool] = False
    """Whether the condition is intentionally unsupported."""

    def __init__(
        self,
        message: str,
        *,
        location: Optional[str] = None,
        offset: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.location = location
        self.offset = offset

    def __str__(self) -> str:
        message = super().__str__()
        if self.offset is None:
            return message
        return f"{message} (offset: {self.offset})."


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


class SignatureMismatchError(DecodingError):
    """Raised when a file signature differs from the expected value."""

    def __init__(
        self,
        actual: bytes,
        expected: bytes,
        *,
        location: Optional[str] = None,
        offset: Optional[int] = None,
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

    def __init__(
        self,
        *,
        location: Optional[str] = None,
        offset: Optional[int] = None,
    ) -> None:
        super().__init__(self._message(), location=location, offset=offset)

    def _message(self) -> str:
        return "Invalid binary structure."


class SafetyLimitError(BinaryStructureError):
    """Raised when a decoded value exceeds a safety limit."""

    def __init__(
        self,
        subject: str,
        count: int,
        maximum: int,
        *,
        location: Optional[str] = None,
        offset: Optional[int] = None,
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


class AnimationError(ScFileException):
    """Raised when animation cannot be applied to a model."""

    ...


class RegistryError(ScFileException):
    """Raised when registry lookup or registration fails."""

    ...


class RegionError(ScFileException):
    """Base exception for region operations."""

    ...


class RegionFileError(RegionError):
    """Raised when a region file fails to decode."""

    def __init__(
        self,
        location: str,
    ) -> None:
        super().__init__("Region file failed to decode.", location=location)


class MergeInterrupted(RegionError):
    """Raised when region merge is interrupted by user."""

    def __init__(self) -> None:
        super().__init__("Merge interrupted.")
