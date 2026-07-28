"""
MCSA decoding exceptions.
"""

from typing import Optional

from scfile.exceptions import DecodingError


class ModelVersionError(DecodingError):
    """Raised when a model version is not supported."""

    unsupported = True

    def __init__(
        self,
        version: float,
        *,
        location: Optional[str] = None,
        offset: Optional[int] = None,
    ) -> None:
        super().__init__(
            f"Unsupported model version: {version}.",
            location=location,
            offset=offset,
        )
        self.version = version
