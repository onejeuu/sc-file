import os
import pathlib
from typing import Iterable, Iterator, NamedTuple, Optional, Sequence, TypeAlias

from .enums import FileFormat


Formats: TypeAlias = Sequence[FileFormat]

Path = pathlib.Path
PathLike: TypeAlias = str | Path | os.PathLike[str]

Output: TypeAlias = Optional[Path]
OutputLike: TypeAlias = Optional[PathLike]

FilesWhitelist: TypeAlias = Iterable[str]
FilesPaths: TypeAlias = Iterable[Path]
FilesSources: TypeAlias = Iterable[PathLike]


class FileEntry(NamedTuple):
    root: str
    path: str
    relpath: str


FilesWalk: TypeAlias = Iterator[FileEntry]
