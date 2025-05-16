"""
Base class for all processable files.
"""

from abc import ABC
from typing import Optional

from scfile.core.context import UserOptions
from scfile.core.io.base import DEFAULT_BYTES_ORDER
from scfile.enums import ByteOrder, FileFormat


class BaseFile(ABC):
    format: FileFormat
    order: ByteOrder = DEFAULT_BYTES_ORDER
    signature: Optional[bytes] = None
    options: UserOptions
