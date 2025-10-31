from scfile.consts import FileSignature
from scfile.core import FileEncoder, TextureContent
from scfile.enums import F, FileFormat
from scfile.formats.dds.enums import DXGIDimension, DXGIFormat
from scfile.structures.texture import TextureType

from .header import DDS
from .mask import BGRA8, RGBA8


class DdsEncoder(FileEncoder[TextureContent[TextureType]]):
    format = FileFormat.DDS
    signature = FileSignature.DDS

    def serialize(self):
        self._add_header()
        self._add_pixelformat()
        self._add_caps()

        if self.data.fourcc == b"DX10":
            self._add_dxgi()

        self.write(self.data.texture.image)

    def _add_header(self):
        self._writeb(
            f"{7}{F.U32}",
            DDS.HEADER.SIZE,  # dwSize
            self._flags,  # dwFlags
            self.data.height,  # dwHeight
            self.data.width,  # dwWidth
            self._pitch_or_linear_size,  # dwPitchOrLinearSize
            0,  # dwDepth
            self.data.mipmap_count,  # dwMipMapCount
        )
        self._writenull(size=4 * 11)  # dwReserved1[11]

    def _add_pixelformat(self):
        self._writeb(F.U32, DDS.PF.SIZE)  # dwSize

        if self.data.is_compressed:
            self._add_pf_fourcc()
        else:
            self._add_pf_rgb()

    def _add_pf_fourcc(self):
        self._writeb(F.U32, DDS.PF.FLAG.FOURCC)  # dwFlags
        self.write(self.data.fourcc)  # dwFourCC
        self._writenull(size=4 * 5)  # dwRGBBitCount, RGBA bit masks (unused)

    def _add_pf_rgb(self):
        self._writeb(F.U32, DDS.PF.RGB)  # dwFlags
        self._writenull(size=4)  # dwFourCC (unused)
        self._writeb(F.U32, DDS.PF.BIT_COUNT)  # dwRGBBitCount

        bitmask = BGRA8 if self.data.fourcc == b"BGRA8" else RGBA8  # not best realization...
        self._writeb(F.U32 * 4, *bitmask)  # RGBA bit masks

    def _add_caps(self):
        self._writeb(
            f"{2}{F.U32}",
            DDS.CAPS1,  # dwCaps1
            self._caps2,  # dwCaps2
        )
        self._writenull(size=4 * 3)  # dwCaps3, dwCaps4, Reserved

    def _add_dxgi(self):
        self._writeb(
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
