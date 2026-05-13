"""
Base class for all processable files.
"""

from abc import ABC
from typing import Optional, TypeVar

from scfile.enums import ByteOrder, FileFormat

from .context import FileContent, UserOptions
from .io import StructIO


Content = TypeVar("Content", bound=FileContent)


class BaseFile(ABC):
    """Abstract base class providing interface for encoders/decoders."""

    format: FileFormat
    order: ByteOrder = StructIO.order
    signature: Optional[bytes] = None
    options: UserOptions
