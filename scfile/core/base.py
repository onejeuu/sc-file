from abc import ABC
from typing import Optional

from scfile.enums import ByteOrder, FileFormat
from scfile.io.consts import DEFAULT_BYTES_ORDER


class BaseFile(ABC):
    format: FileFormat
    order: ByteOrder = DEFAULT_BYTES_ORDER
    signature: Optional[bytes] = None
