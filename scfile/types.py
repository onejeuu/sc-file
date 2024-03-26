import os
import pathlib
from typing import TypeAlias


PathLike: TypeAlias = str | os.PathLike[str] | pathlib.Path
