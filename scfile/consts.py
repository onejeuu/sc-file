from enum import Enum
from typing import NamedTuple


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


class DDSFormat(Enum):
	DXT1 = b'DXT1'
	DXT5 = b'DXT5'
	RGBA = b'RGBA'
	BIT8 = b'RGBA'


class DDS(NamedTuple):
    CAPS = 0x1
    HEIGHT = 0x2
    WIDTH = 0x4
    FOURCC = 0x4
    PIXELFORMAT = 0x1000
    LINEARSIZE = 0x80000
    RGB = 0x40
    ALPHAPIXELS = 0x1

    A_BITMASK = 0xFF000000
    R_BITMASK = 0x00FF0000
    G_BITMASK = 0x0000FF00
    B_BITMASK = 0x000000FF

    HEADER_SIZE = 124
    BLOCK_SIZE = 4096
    BIT_COUNT = 32
