from enum import IntEnum, auto
from typing import Dict


class Flag(IntEnum):
    """Flag Index"""

    SKELETON = 0
    UV = auto()
    NORMALS = auto()
    FLAG_4 = auto()
    FLAG_5 = auto()
    FLAG_6 = auto()


class McsaFlags:
    def __init__(self, version: float):
        self._version = version
        self._flags: Dict[int, bool] = {}

    @property
    def count(self) -> int:
        return {
            7.0: 4,
            8.0: 5,
            10.0: 6
        }.get(self._version, 0)

    @property
    def named_dict(self):
        return {
            Flag(key).name: value
            for key, value in self._flags.items()
        }

    def __getitem__(self, index: int) -> bool:
        return bool(self._flags.get(index, False))

    def __setitem__(self, index: int, value: bool):
        self._flags[index] = bool(value)

    def __str__(self):
        return str(self.named_dict)
