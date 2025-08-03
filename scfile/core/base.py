"""
Base class for all processable files.
"""

from abc import ABC
from typing import Optional

from scfile.core.context import UserOptions
from scfile.core.io import StructIO
from scfile.enums import ByteOrder, FileFormat


class BaseFile(ABC):
    """Abstract base class providing interface for encoders/decoders."""

    format: FileFormat
    order: ByteOrder = StructIO.order
    signature: Optional[bytes] = None
    options: UserOptions
