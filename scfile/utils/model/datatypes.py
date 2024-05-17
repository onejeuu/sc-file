from dataclasses import dataclass
from typing import Self


@dataclass
class Vector:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __sub__(self, vec: Self):
        return Vector(self.x - vec.x, self.y - vec.y, self.z - vec.z)


@dataclass
class Texture:
    u: float = 0.0
    v: float = 0.0


@dataclass
class Polygon:
    a: int = 0
    b: int = 0
    c: int = 0

    def __lshift__(self, offset: int):
        return Polygon(self.a - offset, self.b - offset, self.c - offset)

    def __rshift__(self, offset: int):
        return Polygon(self.a + offset, self.b + offset, self.c + offset)


@dataclass
class Color:
    r: float = 1.0
    g: float = 1.0
    b: float = 1.0
