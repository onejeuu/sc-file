from scfile.consts import Magic
from scfile.enums import StructFormat as F
from scfile.file.data import TextureData

from .._base import FileEncoder
from .structure import DDS


RGBA8 = [0xFF, 0xFF00, 0xFF0000, 0xFF]


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

        self.b.writen(1)  # Depth
        self.b.writeb(F.U32, 1)  # MipMapsCount
        self.b.writen(11)  # Reserved

        self.b.writeb(F.U32, DDS.PF.SIZE)

        if self.compressed:
            self.b.writeb(F.U32, DDS.PF.FLAG.FOURCC)
            self.b.write(self.data.fourcc)  # FourCC
            self.b.writen(5)  # BitCount & BitMasks

        else:
            self.b.writeb(F.U32, DDS.PF.RGB_FLAGS)
            self.b.writen(1)  # FourCC
            self.b.writeb(F.U32, DDS.PF.BIT_COUNT)  # BitCount

            # BitMasks
            for mask in RGBA8:
                self.b.writeb(F.U32, mask)

        self.b.writeb(F.U32, DDS.TEXTURE | DDS.COMPLEX | DDS.MIPMAP)  # Caps1
        self.b.writeb(F.U32, self.cubemap)  # Caps2
        self.b.writen(3)  # Reserved

        self.b.write(self.data.image)

    @property
    def compressed(self) -> bool:
        return b"DXT" in self.data.fourcc

    @property
    def flags(self) -> int:
        if self.compressed:
            return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.LINEARSIZE
        return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.PITCH

    @property
    def pitch(self) -> int:
        bytes_per_pixel = 4
        aligned_width = (self.data.width * bytes_per_pixel + 3) & ~3
        return aligned_width

    @property
    def pitch_or_linear_size(self) -> int:
        if self.compressed:
            return self.data.linear_size
        return self.pitch

    @property
    def cubemap(self) -> int:
        return 0
