"""
OL decoding exceptions.
"""

from typing import Optional

from scfile.exceptions import DecodingError


class TextureFormatError(DecodingError):
    """Raised when a texture format is not supported."""

    unsupported = True

    def __init__(
        self,
        format: bytes,
        *,
        location: Optional[str] = None,
        offset: Optional[int] = None,
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
        location: Optional[str] = None,
        offset: Optional[int] = None,
    ) -> None:
        super().__init__(
            f"Unsupported texture kind: {kind}.",
            location=location,
            offset=offset,
        )
        self.kind = kind
