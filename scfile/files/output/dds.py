from dataclasses import dataclass

from scfile.consts import Magic
from scfile.utils.dds.bitmasks import BITMASKS
from scfile.utils.dds.structure import DDS

from .base import BaseOutputFile, OutputData


@dataclass
class DdsOutputData(OutputData):
    width: int
    height: int
    linear_size: int
    fourcc: bytes
    is_cubemap: bool
    image: bytes


class DdsFile(BaseOutputFile[DdsOutputData]):

    magic = Magic.DDS

    def write(self) -> None:
        self._write(DDS.HEADER.SIZE)
        self._write(self.flags)
        self._write(self.data.height)
        self._write(self.data.width)
        self._write(self.pitch_or_linear_size)
        self._write_null(1) # Depth
        self._write(1) # MipMapsCount
        self._write_null(11) # Reserved

        self._write(DDS.PF.SIZE)
        if self.compressed:
            self._write(DDS.PF.FLAG.FOURCC)
            self._raw_write(self.data.fourcc) # FourCC
            self._write_null(5)

        else:
            self._write(DDS.PF.RGB_FLAGS)
            self._write_null(1) # FourCC
            self._write(DDS.PF.BIT_COUNT)

            for mask in BITMASKS(self.data.fourcc):
                self._write(mask)

        self._write(DDS.TEXTURE | DDS.COMPLEX | DDS.MIPMAP) # Caps1
        self._write(self.cubemap) # Caps2
        self._write_null(3) # Reserved

        self._raw_write(self.data.image)

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
        if self.data.is_cubemap:
            return DDS.CUBEMAPS
        return 0
