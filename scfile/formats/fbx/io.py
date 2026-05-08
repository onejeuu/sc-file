from typing import Any

import numpy as np

from scfile.core.io import StructBytesIO
from scfile.enums import F

from .enums import PropertyType


class FbxFileIO(StructBytesIO):
    def _write_property(self, value: Any):
        if isinstance(value, bool):
            self._writeb(F.U8, PropertyType.BOOL)
            self._writeb(F.U8, 1 if value else 0)
            return

        if isinstance(value, int):
            self._writeb(F.U8, PropertyType.INT32)
            self._writeb(F.I32, value)
            return

        if isinstance(value, np.integer):
            self._writeb(F.U8, PropertyType.INT64)
            self._writeb(F.I64, int(value))
            return

        if isinstance(value, (float, np.floating)):
            self._writeb(F.U8, PropertyType.DOUBLE)
            self._writeb(F.F64, value)
            return

        if isinstance(value, (bytes, str)):
            if isinstance(value, str):
                value = value.encode("utf-8")
            self._writeb(F.U8, PropertyType.STRING)
            self._writeb(F.U32, len(value))
            self.write(value)
            return

        if isinstance(value, np.ndarray):
            self._write_array_property(value)
            return

        if isinstance(value, list):
            self._write_array_property(np.array(value, dtype=np.float64))
            return

        # TODO: typings
        raise TypeError(f"Unsupported property type: {type(value)}!!!")

    def _write_array_property(self, arr: np.ndarray):
        if arr.dtype == np.float32:
            self._writeb(F.U8, PropertyType.ARRAY_FLOAT)
            self._writeb(F.U32, len(arr))
            self._writeb(F.U32, 0)  # encoding
            self._writeb(F.U32, len(arr) * 4)  # compressedLen
            self.write(arr.tobytes())
            return

        if arr.dtype == np.float64:
            self._writeb(F.U8, PropertyType.ARRAY_DOUBLE)
            self._writeb(F.U32, len(arr))
            self._writeb(F.U32, 0)  # encoding
            self._writeb(F.U32, len(arr) * 8)  # compressedLen
            self.write(arr.tobytes())
            return

        if arr.dtype == np.int64:
            self._writeb(F.U8, PropertyType.ARRAY_INT64)
            self._writeb(F.U32, len(arr))
            self._writeb(F.U32, 0)  # encoding
            self._writeb(F.U32, len(arr) * 8)  # compressedLen
            self.write(arr.tobytes())
            return

        if arr.dtype == np.int32:
            self._writeb(F.U8, PropertyType.ARRAY_INT32)
            self._writeb(F.U32, len(arr))
            self._writeb(F.U32, 0)  # encoding
            self._writeb(F.U32, len(arr) * 4)  # compressedLen
            self.write(arr.tobytes())
            return

        # TODO: typings
        raise TypeError(f"Unsupported array type: {type(arr)}!!!")
