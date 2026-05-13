import os
import pathlib
from typing import Iterator, Optional, Sequence, Tuple, TypeAlias


Path = pathlib.Path
PathLike: TypeAlias = str | Path | os.PathLike[str]

Output: TypeAlias = Optional[Path]
OutputLike: TypeAlias = Optional[PathLike]

FilesPaths: TypeAlias = Sequence[Path]
FilesSources: TypeAlias = Sequence[PathLike]
FilesIter: TypeAlias = Iterator[Tuple[Path, Path]]
