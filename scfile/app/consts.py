from pathlib import Path

from scfile.enums import FileFormat
from scfile.types import Formats


ORGANIZATION: str = "onejeuu"
APPLICATION: str = "scfile"
TITLE: str = "scfile"

DEFAULT_OUTPUT: Path = Path.home() / APPLICATION / "export"

UPDATE_CHECK_TIMEOUT_SECS: float = 5.0

MODEL_FORMAT_ORDER: Formats = (
    FileFormat.OBJ,
    FileFormat.GLB,
    FileFormat.FBX,
)
