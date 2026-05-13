import os
import pathlib
from typing import Iterator, NamedTuple, Optional, Sequence, TypeAlias

from .enums import FileFormat


Formats: TypeAlias = Sequence[FileFormat]

Path = pathlib.Path
PathLike: TypeAlias = str | Path | os.PathLike[str]

Output: TypeAlias = Optional[Path]
OutputLike: TypeAlias = Optional[PathLike]

Sources: TypeAlias = Sequence[str]
FilesWhitelist: TypeAlias = Sequence[str]
FilesPaths: TypeAlias = Sequence[Path]
FilesSources: TypeAlias = Sequence[PathLike]


class FileEntry(NamedTuple):
    root: str
    path: str
    relpath: str


FilesWalk: TypeAlias = Iterator[FileEntry]
# SuffixesWhitelist: TypeAlias = tuple[str, ...]
