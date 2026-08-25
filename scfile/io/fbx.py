"""Structured I/O extensions for FBX."""

from struct import Struct
from typing import assert_never

import numpy as np
from numpy.typing import NDArray

from scfile.formats.fbx.enums import PropertyType as Prop

from .base import StructWriter


type Scalar = bool | int | float | str | bytes | np.integer | np.floating
type Float32Array = NDArray[np.float32]
type Float64Array = NDArray[np.float64]
type Int32Array = NDArray[np.int32]
type Int64Array = NDArray[np.int64]
type UInt32Array = NDArray[np.uint32]
type Array = Float32Array | Float64Array | Int32Array | Int64Array
type Value = Scalar | Array | list[Scalar]
type Cluster = tuple[Int32Array, Float64Array]


_NODE = Struct("<IIIB")
_FIELDS = Struct("<III")
_BOOL = Struct("<BB")
_INT32 = Struct("<Bi")
_INT64 = Struct("<Bq")
_DOUBLE = Struct("<Bd")
_STRING = Struct("<BI")
_ARRAY = Struct("<BIII")
_NULL_NODE = bytes(_NODE.size)


class FbxWriter(StructWriter):
    def header(
        self,
        end: int,
        properties: int,
        length: int,
        name: bytes | None = None,
    ) -> None:
        if name is None:
            self.write(_FIELDS.pack(end, properties, length))
        else:
            self.write(_NODE.pack(end, properties, length, len(name)) + name)

    def matrix(
        self,
        value: Float32Array,
    ) -> Float64Array:
        return value.T.astype(np.float64, copy=False).flatten()

    def property(
        self,
        value: Value,
    ) -> None:
        self.write(self._property(value))

    def leaf(
        self,
        name: bytes,
        properties: list[Value],
        root: bool = False,
    ) -> None:
        self.write(self._leaf(self.tell(), name, properties, root))

    def animation_curve(
        self,
        curve: np.int64,
        times: bytes,
        values: Float32Array,
        attributes: bytes,
        references: bytes,
        version: int,
    ) -> None:
        properties: list[Value] = [curve, b"\x00\x01AnimCurve", b""]
        payload = self._properties(properties)
        position = self.tell() + _NODE.size + len(b"AnimationCurve") + len(payload)
        children: list[bytes] = []

        nodes = (
            (b"Default", self._double(values[0])),
            (b"KeyVer", self._int32(version)),
            (b"KeyTime", times),
            (b"KeyValueFloat", self._array(values)),
            (b"KeyAttrFlags", attributes),
            (b"KeyAttrRefCount", references),
        )
        for name, child_data in nodes:
            child = self._property_leaf(position, name, child_data)
            children.append(child)
            position += len(child)

        end = position + len(_NULL_NODE)
        header = _NODE.pack(end, len(properties), len(payload), len(b"AnimationCurve"))
        self.write(header + b"AnimationCurve" + payload + b"".join(children) + _NULL_NODE)

    def _leaf(
        self,
        position: int,
        name: bytes,
        properties: list[Value],
        root: bool = False,
    ) -> bytes:
        payload = self._properties(properties)
        ending = _NULL_NODE if root else b""
        end = position + _NODE.size + len(name) + len(payload) + len(ending)
        return _NODE.pack(end, len(properties), len(payload), len(name)) + name + payload + ending

    def _property_leaf(
        self,
        position: int,
        name: bytes,
        data: bytes,
    ) -> bytes:
        end = position + _NODE.size + len(name) + len(data)
        return _NODE.pack(end, 1, len(data), len(name)) + name + data

    def _properties(self, values: list[Value]) -> bytes:
        return b"".join(self._property(value) for value in values)

    def curve_data(
        self,
        times: Int64Array,
        attributes: Int32Array,
        references: Int32Array,
    ) -> tuple[bytes, bytes, bytes]:
        return self._array(times), self._array(attributes), self._array(references)

    def _property(
        self,
        value: Value,
    ) -> bytes:
        match value:
            case bool():
                return self._bool(value)
            case int():
                return self._int32(value)
            case np.integer():
                return self._int64(value)
            case float() | np.floating():
                return self._double(value)
            case str() | bytes():
                return self._string(value)
            case np.ndarray():
                return self._array(value)
            case list():
                return self._array(np.array(value, dtype=np.float64))
            case _:
                assert_never(value)

    def _bool(self, value: bool) -> bytes:
        return _BOOL.pack(Prop.BOOL, value)

    def _int32(self, value: int) -> bytes:
        return _INT32.pack(Prop.INT32, value)

    def _int64(self, value: np.integer) -> bytes:
        return _INT64.pack(Prop.INT64, value)

    def _double(self, value: float | np.floating) -> bytes:
        return _DOUBLE.pack(Prop.DOUBLE, value)

    def _string(self, value: str | bytes) -> bytes:
        if isinstance(value, str):
            value = value.encode("utf-8")
        return _STRING.pack(Prop.STRING, len(value)) + value

    def _array(self, arr: Array) -> bytes:
        prop, size = 0, 0

        match arr.dtype:
            case np.float32:
                prop, size = Prop.ARRAY_FLOAT, 4
            case np.float64:
                prop, size = Prop.ARRAY_DOUBLE, 8
            case np.int64:
                prop, size = Prop.ARRAY_INT64, 8
            case np.int32:
                prop, size = Prop.ARRAY_INT32, 4

        return _ARRAY.pack(prop, len(arr), 0, len(arr) * size) + arr.tobytes()

    def polygon_indices(
        self,
        polygons: UInt32Array,
    ) -> Int32Array:
        indices = polygons.flatten().astype(np.int32)
        indices[2::3] = -indices[2::3] - 1
        return indices
