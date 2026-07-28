"""
MS3D encoding exceptions.
"""

from typing import Optional

from scfile.exceptions import EncodingError


class Ms3dCapacityError(EncodingError):
    """Raised when a model exceeds MS3D format capacity."""

    unsupported = True

    def __init__(
        self,
        subject: str,
        count: int,
        capacity: int,
        *,
        location: Optional[str] = None,
        offset: Optional[int] = None,
    ) -> None:
        super().__init__(
            f"MS3D capacity exceeded: {count:,} {subject} (max: {capacity:,}).",
            location=location,
            offset=offset,
        )
        self.subject = subject
        self.count = count
        self.capacity = capacity
