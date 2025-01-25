from abc import ABC
from dataclasses import dataclass, fields
from typing import Iterator, TypeVar


T = TypeVar("T", bound="VectorBase")


@dataclass
class VectorBase(ABC):
    def __iter__(self) -> Iterator:
        return iter(getattr(self, field.name) for field in fields(self))

    def __add__(self: T, other: T) -> T:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(*(a + b for a, b in zip(self, other)))

    def __sub__(self: T, other: T) -> T:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(*(a - b for a, b in zip(self, other)))

    def __rshift__(self: T, offset: float) -> T:
        return self.__class__(*(value + offset for value in self))

    def __lshift__(self: T, offset: float) -> T:
        return self.__class__(*(value - offset for value in self))


@dataclass
class Vector2(VectorBase):
    u: float = 0.0
    v: float = 0.0


@dataclass
class Vector3(VectorBase):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Vector4(VectorBase):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 0.0


@dataclass
class Polygon(VectorBase):
    a: int = 0
    b: int = 0
    c: int = 0


@dataclass
class Color(VectorBase):
    r: float = 0.8
    g: float = 0.8
    b: float = 0.8
