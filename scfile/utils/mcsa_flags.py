from enum import IntEnum, auto
from typing import Dict


class Flags(IntEnum):
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
        return  (self[Flags.FLAG_5]) or \
                (self[Flags.FLAG_3] and not self[Flags.UV]) or \
                (self[Flags.UV] and not self[Flags.FLAG_3])
