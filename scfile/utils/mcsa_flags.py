from enum import IntEnum, auto
from typing import Dict


class Flag(IntEnum):
    """Flag Index"""

    SKELETON = 0
    UV = auto()
    VERTEX_WEIGHT = auto()
    NORMALS = auto()
    FLAG_5 = auto()
    FLAG_6 = auto()
    FLAG_7 = auto()
    FLAG_8 = auto()
    FLAG_9 = auto()
    FLAG_10 = auto()


class McsaFlags:
    def __init__(self, version: float):
        self._version = version
        self._flags: Dict[int, bool] = {}

    @property
    def count(self) -> int:
        return int(self._version - 3.0)

    @property
    def unsupported(self):
        return (
            self[Flag.FLAG_5] or \
            self[Flag.VERTEX_WEIGHT] and not self[Flag.UV] or \
            self[Flag.UV] and not self[Flag.VERTEX_WEIGHT]
        )

    def __getitem__(self, index: int) -> bool:
        return bool(self._flags.get(index, False))

    def __setitem__(self, index: int, value: int):
        self._flags[index] = bool(value)

    def __str__(self):
        return str(dict(self._flags.items()))
