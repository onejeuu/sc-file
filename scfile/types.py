import os
import pathlib
from typing import Optional, TypeAlias


PathLike: TypeAlias = str | os.PathLike[str] | pathlib.Path
OutputDir: TypeAlias = Optional[PathLike]
