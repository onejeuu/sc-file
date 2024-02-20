import os
from pathlib import Path
from typing import TypeAlias


PathLike: TypeAlias = str | os.PathLike[str] | Path
