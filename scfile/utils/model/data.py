import math
from dataclasses import dataclass
from typing import Self


@dataclass
class Vector:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __add__(self, vec: Self):
        return Vector(self.x + vec.x, self.y + vec.y, self.z + vec.z)

    def __sub__(self, vec: Self):
        return Vector(self.x - vec.x, self.y - vec.y, self.z - vec.z)

    def __truediv__(self, scalar: float):
        return Vector(self.x / scalar, self.y / scalar, self.z / scalar)

    def __mul__(self, scalar: float):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    @property
    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        if self.length == 0:
            return self
        return self / self.length


@dataclass
class Texture:
    u: float = 0.0
    v: float = 0.0

    def __iter__(self):
        return iter((self.u, self.v))


@dataclass
class Polygon:
    a: int = 0
    b: int = 0
    c: int = 0

    def __iter__(self):
        return iter((self.a, self.b, self.c))

    def __rshift__(self, offset: int):
        return Polygon(self.a + offset, self.b + offset, self.c + offset)

    def __lshift__(self, offset: int):
        return Polygon(self.a - offset, self.b - offset, self.c - offset)


@dataclass
class Color:
    r: float = 0.8
    g: float = 0.8
    b: float = 0.8

    def __iter__(self):
        return iter((self.r, self.g, self.b))
