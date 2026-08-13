from typing import override

from scfile.consts import FormatSignature
from scfile.structures.content import TextureContent
from scfile.core import Encoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.formats.dds.enums import DXGIDimension, DXGIFormat

from .enums import BGRA8, RGBA8
from .header import DDS


class DdsEncoder(Encoder[TextureContent]):
    format = FileFormat.DDS
    signature = FormatSignature.DDS
    order = ByteOrder.LITTLE

    content_type = TextureContent

    @override
    def _serialize(self):
        self._add_header()
        self._add_pixelformat()
        self._add_caps()

        if self.data.fourcc == b"DX10":
            self._add_dxgi()

        self.io.write(self.data.texture.image)

    def _add_header(self):
        self.io.value(
            f"{7}{F.U32}",
            DDS.HEADER.SIZE,  # dwSize
            self._flags,  # dwFlags
            self.data.height,  # dwHeight
            self.data.width,  # dwWidth
            self._pitch_or_linear_size,  # dwPitchOrLinearSize
            0,  # dwDepth
            self.data.mipmap_count,  # dwMipMapCount
        )
        self.io.null(size=4 * 11)  # dwReserved1[11]

    def _add_pixelformat(self):
        self.io.value(F.U32, DDS.PF.SIZE)  # dwSize

        if self.data.is_compressed:
            self._add_pf_fourcc()
        else:
            self._add_pf_rgb()

    def _add_pf_fourcc(self):
        self.io.value(F.U32, DDS.PF.FLAG.FOURCC)  # dwFlags
        self.io.write(self.data.fourcc)  # dwFourCC
        self.io.null(size=4 * 5)  # dwRGBBitCount, RGBA bit masks (unused)

    def _add_pf_rgb(self):
        self.io.value(F.U32, DDS.PF.RGB)  # dwFlags
        self.io.null(size=4)  # dwFourCC (unused)
        self.io.value(F.U32, DDS.PF.BIT_COUNT)  # dwRGBBitCount

        bitmask = BGRA8 if self.data.fourcc == b"BGRA8" else RGBA8
        self.io.value(F.U32 * 4, *bitmask)  # RGBA bit masks

    def _add_caps(self):
        self.io.value(
            f"{2}{F.U32}",
            DDS.CAPS1,  # dwCaps1
            self._caps2,  # dwCaps2
        )
        self.io.null(size=4 * 3)  # dwCaps3, dwCaps4, Reserved

    def _add_dxgi(self):
        self.io.value(
            f"{5}{F.U32}",
            DXGIFormat.FLOAT_R32G32B32A32,  # dxgiFormat
            DXGIDimension.TEXTURE2D,  # resourceDimension
            0,  # miscFlag
            1,  # arraySize
            0,  # miscFlags2
        )

    @property
    def _flags(self) -> int:
        if self.data.is_compressed:
            return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.LINEARSIZE
        return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.PITCH

    @property
    def _pitch(self) -> int:
        bytes_per_pixel = 4
        aligned_width = (self.data.width * bytes_per_pixel + 3) & ~3
        return aligned_width

    @property
    def _pitch_or_linear_size(self) -> int:
        if self.data.is_compressed:
            return self.data.texture.linear_size
        return self._pitch

    @property
    def _caps2(self) -> int:
        if self.data.is_cubemap:
            return DDS.CUBEMAPS
        return 0
