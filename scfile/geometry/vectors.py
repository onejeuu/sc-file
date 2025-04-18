from abc import ABC
from dataclasses import dataclass
from typing import Iterator, Self


@dataclass
class BaseVector(ABC):
    def __iter__(self) -> Iterator[float]:
        return iter(self.__dict__.values())

    def __add__(self: Self, other: Self) -> Self:
        return self.__class__(*(a + b for a, b in zip(self, other)))

    def __sub__(self: Self, other: Self) -> Self:
        return self.__class__(*(a - b for a, b in zip(self, other)))

    def __rshift__(self: Self, offset: float) -> Self:
        return self.__class__(*(value + offset for value in self))

    def __lshift__(self: Self, offset: float) -> Self:
        return self.__class__(*(value - offset for value in self))


@dataclass
class Vector2(BaseVector):
    u: float = 0.0
    v: float = 0.0


@dataclass
class Vector3(BaseVector):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Vector4(BaseVector):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 0.0


@dataclass
class Quaternion(BaseVector):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0


@dataclass
class Polygon(BaseVector):
    a: int = 0
    b: int = 0
    c: int = 0
