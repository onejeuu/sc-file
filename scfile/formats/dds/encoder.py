from scfile.core.context import TextureContext
from scfile.core.encoder import FileEncoder
from scfile.enums import FileFormat
from scfile.enums import StructFormat as F

from .header import DDS
from .mask import BGRA8, RGBA8


class DdsEncoder(FileEncoder[TextureContext]):
    @property
    def format(self):
        return FileFormat.DDS

    def serialize(self):
        self.b.writeb(F.U32, DDS.HEADER.SIZE)
        self.b.writeb(F.U32, self.flags)
        self.b.writeb(F.U32, self.ctx.height)
        self.b.writeb(F.U32, self.ctx.width)
        self.b.writeb(F.U32, self.pitch_or_linear_size)
        self.b.writenull(size=4)  # Depth
        self.b.writeb(F.U32, self.ctx.mipmap_count)  # MipMapsCount
        self.b.writenull(size=4 * 11)  # Reserved

        self.add_pixelformat()
        self.add_caps()

        self.b.write(self.ctx.image)

    def add_pixelformat(self):
        self.b.writeb(F.U32, DDS.PF.SIZE)

        if self.is_compressed:
            self.add_pf_fourcc()

        else:
            self.add_pf_rgb()

    def add_pf_fourcc(self):
        self.b.writeb(F.U32, DDS.PF.FLAG.FOURCC)
        self.b.write(self.ctx.fourcc)  # FourCC
        self.b.writenull(size=4 * 5)  # BitCount & BitMasks

    def add_pf_rgb(self):
        self.b.writeb(F.U32, DDS.PF.RGB)
        self.b.writenull(size=4)  # FourCC
        self.b.writeb(F.U32, DDS.PF.BIT_COUNT)  # BitCount
        self.b.writeb(F.U32 * 4, BGRA8 if self.ctx.fourcc == b"BGRA8" else RGBA8)  # BitMask

    def add_caps(self):
        self.b.writeb(F.U32, self.caps)  # Caps1
        self.b.writeb(F.U32, self.cubemap)  # Caps2
        self.b.writenull(size=4 * 3)  # Reserved

    @property
    def is_compressed(self) -> bool:
        return self.ctx.fourcc in (b"DXT1", b"DXT3", b"DXT5", b"ATI2")

    @property
    def flags(self) -> int:
        if self.is_compressed:
            return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.LINEARSIZE
        return DDS.HEADER.FLAGS | DDS.HEADER.FLAG.PITCH

    @property
    def pitch(self) -> int:
        bytes_per_pixel = 4
        aligned_width = (self.ctx.width * bytes_per_pixel + 3) & ~3
        return aligned_width

    @property
    def pitch_or_linear_size(self) -> int:
        if self.is_compressed:
            return self.ctx.linear_size
        return self.pitch

    @property
    def caps(self):
        if self.ctx.is_hdri:
            return DDS.CAPS | DDS.CUBEMAP
        return DDS.CAPS

    @property
    def cubemap(self) -> int:
        if self.ctx.is_hdri:
            return DDS.CUBEMAPS
        return 0
