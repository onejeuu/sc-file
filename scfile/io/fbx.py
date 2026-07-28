from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray

from scfile.enums import F
from scfile.formats.fbx.enums import PropertyType as Prop

from .structio import StructWriter


Scalar: TypeAlias = bool | int | float | str | bytes | np.integer | np.floating
Float32Array: TypeAlias = NDArray[np.float32]
Float64Array: TypeAlias = NDArray[np.float64]
Int32Array: TypeAlias = NDArray[np.int32]
Int64Array: TypeAlias = NDArray[np.int64]
Array: TypeAlias = Float32Array | Float64Array | Int32Array | Int64Array
Value: TypeAlias = Scalar | Array | list[Scalar]


class FbxWriter(StructWriter):
    def property(
        self,
        value: Value,
    ) -> None:
        match value:
            case bool():
                self._bool(value)
            case int():
                self._int32(value)
            case np.integer():
                self._int64(value)
            case float() | np.floating():
                self._double(value)
            case str() | bytes():
                self._string(value)
            case np.ndarray():
                self._array(value)
            case list():
                self._array(np.array(value, dtype=np.float64))

    # Serialize individual FBX property payloads selected by property()
    def _bool(self, value: bool) -> None:
        self.value(F.U8, Prop.BOOL)
        self.value(F.U8, 1 if value else 0)

    def _int32(self, value: int) -> None:
        self.value(F.U8, Prop.INT32)
        self.value(F.I32, value)

    def _int64(self, value: np.integer) -> None:
        self.value(F.U8, Prop.INT64)
        self.value(F.I64, int(value))

    def _double(self, value: float | np.floating) -> None:
        self.value(F.U8, Prop.DOUBLE)
        self.value(F.F64, float(value))

    def _string(self, value: str | bytes) -> None:
        if isinstance(value, str):
            value = value.encode("utf-8")
        self.value(F.U8, Prop.STRING)
        self.value(F.U32, len(value))
        self.write(value)

    def _array(self, arr: Array) -> None:
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

        self.value(F.U8, prop)
        self.value(F.U32, len(arr))
        self.value(F.U32, 0)
        self.value(F.U32, len(arr) * size)
        self.write(arr.tobytes())
