from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray

from scfile.core import StructIO
from scfile.enums import F

from .enums import PropertyType as Prop


Scalar: TypeAlias = bool | int | float | str | bytes | np.integer | np.floating
Float32Array: TypeAlias = NDArray[np.float32]
Float64Array: TypeAlias = NDArray[np.float64]
Int32Array: TypeAlias = NDArray[np.int32]
Int64Array: TypeAlias = NDArray[np.int64]
Array: TypeAlias = Float32Array | Float64Array | Int32Array | Int64Array
Value: TypeAlias = Scalar | Array | list[Scalar]


class FbxFileIO(StructIO):
    def _write_property(self, value: Value) -> None:
        match value:
            case bool():
                self._write_bool(value)
            case int():
                self._write_int32(value)
            case np.integer():
                self._write_int64(value)
            case float() | np.floating():
                self._write_double(value)
            case str() | bytes():
                self._write_string(value)
            case np.ndarray():
                self._write_array(value)
            case list():
                self._write_array(np.array(value, dtype=np.float64))

    def _write_bool(self, value: bool) -> None:
        self._writeb(F.U8, Prop.BOOL)
        self._writeb(F.U8, 1 if value else 0)

    def _write_int32(self, value: int) -> None:
        self._writeb(F.U8, Prop.INT32)
        self._writeb(F.I32, value)

    def _write_int64(self, value: np.integer) -> None:
        self._writeb(F.U8, Prop.INT64)
        self._writeb(F.I64, int(value))

    def _write_double(self, value: float | np.floating) -> None:
        self._writeb(F.U8, Prop.DOUBLE)
        self._writeb(F.F64, float(value))

    def _write_string(self, value: str | bytes) -> None:
        if isinstance(value, str):
            value = value.encode("utf-8")
        self._writeb(F.U8, Prop.STRING)
        self._writeb(F.U32, len(value))
        self.write(value)

    def _write_array(self, arr: Array) -> None:
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

        self._writeb(F.U8, prop)
        self._writeb(F.U32, len(arr))
        self._writeb(F.U32, 0)
        self._writeb(F.U32, len(arr) * size)
        self.write(arr.tobytes())
