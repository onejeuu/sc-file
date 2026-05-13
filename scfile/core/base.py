"""
Base class for all processable files.
"""

from abc import ABC
from typing import Optional

from scfile.enums import ByteOrder, FileFormat

from .context import UserOptions
from .io import StructIO


class BaseFile(ABC):
    """Abstract base class providing interface for encoders/decoders."""

    format: FileFormat
    order: ByteOrder = StructIO.order
    signature: Optional[bytes] = None
    options: UserOptions
