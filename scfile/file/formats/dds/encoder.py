from scfile.consts import Magic
from scfile.enums import StructFormat as F
from scfile.file.base import FileEncoder
from scfile.file.data import TextureData

from .header import DDS
from .masks import BGRA8, RGBA8, Mask


class DdsEncoder(FileEncoder[TextureData]):
    @property
    def magic(self):
        return Magic.DDS

    def serialize(self):
        self.b.writeb(F.U32, DDS.HEADER.SIZE)
        self.b.writeb(F.U32, self.flags)
        self.b.writeb(F.U32, self.data.height)
        self.b.writeb(F.U32, self.data.width)
        self.b.writeb(F.U32, self.pitch_or_linear_size)
        self.b.writen(count=1)  # Depth
        self.b.writeb(F.U32, self.data.mipmap_count)  # MipMapsCount
        self.b.writen(count=11)  # Reserved

        self._add_pixelformat()
        self._add_caps()

        self.b.write(self.data.image)

    def _add_pixelformat(self):
        self.b.writeb(F.U32, DDS.PF.SIZE)

        if self.is_compressed:
            self._add_pf_fourcc()

        else:
            self._add_pf_rgb()

    def _add_pf_fourcc(self):
        self.b.writeb(F.U32, DDS.PF.FLAG.FOURCC)
        self.b.write(self.data.fourcc)  # FourCC
        self.b.writen(5)  # BitCount & BitMasks

    def _add_pf_rgb(self):
        self.b.writeb(F.U32, DDS.PF.RGB_FLAGS)
        self.b.writen(count=1)  # FourCC
        self.b.writeb(F.U32, DDS.PF.BIT_COUNT)  # BitCount

        # BitMasks
        mask: Mask = RGBA8

        if self.data.fourcc == b"BGRA8":
            mask = BGRA8

        self.b.writeb(F.U32 * 4, *mask)

    def _add_caps(self):
        self.b.writeb(F.U32, DDS.TEXTURE | DDS.COMPLEX | DDS.MIPMAP)  # Caps1
        self.b.writeb(F.U32, self.cubemap)  # Caps2
        self.b.writen(count=3)  # Reserved

    @property
    def is_compressed(self) -> bool:
        return self.data.fourcc in (b"DXT1", b"DXT3", b"DXT5", b"ATI2")

    @property
    def flags(self) -> int:
        if self.is_compressed:
            return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.LINEARSIZE
        return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.PITCH

    @property
    def pitch(self) -> int:
        bytes_per_pixel = 4
        aligned_width = (self.data.width * bytes_per_pixel + 3) & ~3
        return aligned_width

    @property
    def pitch_or_linear_size(self) -> int:
        if self.is_compressed:
            return self.data.linear_size
        return self.pitch

    @property
    def cubemap(self) -> int:
        return 0
