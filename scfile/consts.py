from enum import Enum, IntEnum, auto
from typing import NamedTuple
from dataclasses import dataclass


ROOT_BONE_ID = -1


class Signature(NamedTuple):
    MIC = 0x894D4943
    OL = 0x0A9523FD
    MCSA = 0x4D435341


class Magic(NamedTuple):
    PNG = [0x89, 0x50, 0x4E, 0x47]
    DDS = [0x44, 0x44, 0x53, 0x20]


class Normalization(NamedTuple):
    BYTE = BONE_WEIGHT = 0xFF
    SHORT = VERTEX_LIMIT = 0x8000


class FileSuffix(NamedTuple):
    MIC = ".mic"
    OL = ".ol"
    MCSA = ".mcsa"
    PNG = ".png"
    DDS = ".dds"
    OBJ = ".obj"


class PixelFormatType(IntEnum):
    COMPRESSED = auto()
    UNCOMPRESSED = auto()


@dataclass
class PixelFormat:
    name: bytes
    type: PixelFormatType


class DDSFormat(Enum):
    DXT1 = PixelFormat(b"DXT1", PixelFormatType.COMPRESSED)
    DXT5 = PixelFormat(b"DXT5", PixelFormatType.COMPRESSED)
    RGBA = PixelFormat(b"RGBA", PixelFormatType.UNCOMPRESSED)
    BIT8 = PixelFormat(b"BIT8", PixelFormatType.UNCOMPRESSED)


class DDS(NamedTuple):
    class HEADER(NamedTuple):
        SIZE = 124

        class FLAG(NamedTuple):
            CAPS = 0x1
            HEIGHT = 0x2
            WIDTH = 0x4
            PITCH = 0x8
            PIXELFORMAT = 0x1000
            MIPMAPCOUNT = 0x20000
            LINEARSIZE = 0x80000
            DEPTH = 0x800000

        FLAGS = FLAG.CAPS | FLAG.HEIGHT | FLAG.WIDTH | FLAG.PIXELFORMAT

    class PIXELFORMAT(NamedTuple):
        SIZE = 32
        BIT_COUNT = 32

        class FLAG(NamedTuple):
            ALPHAPIXELS = 0x1
            ALPHA = 0x2
            FOURCC = 0x4
            RGB = 0x40

        class BITMASK(NamedTuple):
            R = 0x00FF0000
            G = 0x0000FF00
            B = 0x000000FF
            A = 0xFF000000

    PF = PIXELFORMAT

    COMPLEX = 0x8
    TEXTURE = 0x1000
    MIPMAP = 0x400000
