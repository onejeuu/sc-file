from enum import IntEnum, auto


class Flag(IntEnum):
    SKELETON = 0
    TEXTURE = auto()
    NORMALS = auto()
    TANGENTS = auto()
    BITANGENTS = auto()
    FLAG_6 = auto()


class McsaFlags:
    def __init__(self):
        self._flags: dict[int, bool] = {}

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
