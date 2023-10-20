from enum import IntEnum, auto
from typing import Dict


class Flag(IntEnum):
    """Flag Index"""

    SKELETON = 0
    UV = auto()
    FLAG_3 = auto()
    FLAG_4 = auto()
    FLAG_5 = auto()


class McsaFlags:
    def __init__(self):
        self._flags: Dict[int, bool] = {}

    def __getitem__(self, index: int) -> bool:
        return bool(self._flags.get(index, 0))

    def __setitem__(self, index: int, value: int):
        self._flags[index] = bool(value)

    def __str__(self):
        return str(dict(self._flags.items()))

    @property
    def unsupported(self):
        return  (self[Flag.FLAG_5]) or \
                (self[Flag.FLAG_3] and not self[Flag.UV]) or \
                (self[Flag.UV] and not self[Flag.FLAG_3])
