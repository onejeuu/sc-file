import os
import pathlib
from typing import Iterator, Optional, Sequence, Tuple, TypeAlias


Path = pathlib.Path

PathLike: TypeAlias = str | Path | os.PathLike[str]

OutputDir: TypeAlias = Optional[Path]

FilesPaths: TypeAlias = Sequence[Path]
FilesIter: TypeAlias = Iterator[Tuple[Path, Path]]
