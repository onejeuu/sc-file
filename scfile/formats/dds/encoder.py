from scfile.consts import FileSignature
from scfile.core import FileEncoder
from scfile.core.context import TextureContent
from scfile.enums import FileFormat
from scfile.enums import StructFormat as F

from .header import DDS
from .mask import BGRA8, RGBA8


class DdsEncoder(FileEncoder[TextureContent]):
    format = FileFormat.DDS
    signature = FileSignature.DDS

    def serialize(self):
        self.writeb(F.U32, DDS.HEADER.SIZE)
        self.writeb(F.U32, self.flags)
        self.writeb(F.U32, self.data.height)
        self.writeb(F.U32, self.data.width)
        self.writeb(F.U32, self.pitch_or_linear_size)
        self.writenull(size=4)  # Depth
        self.writeb(F.U32, self.data.mipmap_count)  # MipMapsCount
        self.writenull(size=4 * 11)  # Reserved

        self.add_pixelformat()
        self.add_caps()

        self.write(self.data.texture.image)

    def add_pixelformat(self):
        self.writeb(F.U32, DDS.PF.SIZE)

        if self.is_compressed:
            self.add_pf_fourcc()

        else:
            self.add_pf_rgb()

    def add_pf_fourcc(self):
        self.writeb(F.U32, DDS.PF.FLAG.FOURCC)
        self.write(self.data.fourcc)  # FourCC
        self.writenull(size=4 * 5)  # BitCount & BitMasks

    def add_pf_rgb(self):
        self.writeb(F.U32, DDS.PF.RGB)
        self.writenull(size=4)  # FourCC
        self.writeb(F.U32, DDS.PF.BIT_COUNT)  # BitCount

        bitmask = BGRA8 if self.data.fourcc == b"BGRA8" else RGBA8
        self.writeb(F.U32 * 4, *bitmask)  # BitMask

    def add_caps(self):
        self.writeb(F.U32, DDS.CAPS)  # Caps1
        self.writeb(F.U32, self.cubemaps)  # Caps2
        self.writenull(size=4 * 3)  # Reserved

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
            return self.data.texture.linear_size
        return self.pitch

    @property
    def cubemaps(self) -> int:
        if self.data.is_cubemap:
            return DDS.CUBEMAPS
        return 0
