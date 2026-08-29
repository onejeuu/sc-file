"""Region coordinate utilities."""

from collections.abc import Callable, Iterable
from typing import NamedTuple, Self


type CancelCheck = Callable[[], bool] | None


class Size(NamedTuple):
    width: int
    height: int


class Offset(NamedTuple):
    left: int
    top: int


class Region(NamedTuple):
    x: int
    z: int

    @classmethod
    def parse(cls, stem: str) -> Self | None:
        try:
            x, z = map(int, stem.split("."))

        except ValueError:
            return None

        return cls(x, z)


class Bounds(NamedTuple):
    left: int
    top: int
    right: int
    bottom: int

    @classmethod
    def parse(cls, regions: Iterable[Region]) -> Self:
        regions = tuple(regions)
        return cls(
            left=min(region.x for region in regions),
            top=min(region.z for region in regions),
            right=max(region.x for region in regions),
            bottom=max(region.z for region in regions),
        )

    def size(self, region: Size) -> Size:
        return Size(
            width=(self.right - self.left + 1) * region.width,
            height=(self.bottom - self.top + 1) * region.height,
        )

    def offset(self, region: Region, size: Size) -> Offset:
        left = (region.x - self.left) * size.width
        top = (region.z - self.top) * size.height
        return Offset(left, top)
