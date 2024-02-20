from typing import NamedTuple, Self


class McsaVersion(NamedTuple):
    version: float
    flags: int

    def __eq__(self, other: Self | float):
        if isinstance(other, McsaVersion):
            return self.version == other.version

        if isinstance(other, float):
            return self.version == other

        return False

class SupportedList(list[McsaVersion]):
    def find(self, target: McsaVersion | float):
        for version in self:
            if version == target:
                return version

SUPPORTED_VERSIONS = SupportedList([
    McsaVersion(7.0, 4),
    McsaVersion(8.0, 5),
    McsaVersion(10.0, 6),
])
