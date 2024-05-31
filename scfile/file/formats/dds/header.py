from enum import IntFlag


class HeaderFlag(IntFlag):
    CAPS = 0x1
    HEIGHT = 0x2
    WIDTH = 0x4
    PITCH = 0x8
    PIXELFORMAT = 0x1000
    MIPMAPCOUNT = 0x20000
    LINEARSIZE = 0x80000
    DEPTH = 0x800000


class Header:
    SIZE = 124
    FLAG = HeaderFlag
    FLAGS = FLAG.CAPS | FLAG.HEIGHT | FLAG.WIDTH | FLAG.PIXELFORMAT | FLAG.MIPMAPCOUNT


class PixelFormatFlag(IntFlag):
    ALPHAPIXELS = 0x1
    ALPHA = 0x2
    FOURCC = 0x4
    RGB = 0x40


class PixelFormat:
    SIZE = 32
    BIT_COUNT = 32
    FLAG = PixelFormatFlag
    RGB_FLAGS = FLAG.RGB | FLAG.ALPHAPIXELS


class CubemapFlag(IntFlag):
    POSITIVE_X = POSX = 0x400
    NEGATIVE_X = NEGX = 0x800
    POSITIVE_Y = POSY = 0x1000
    NEGATIVE_Y = NEGY = 0x2000
    POSITIVE_Z = POSZ = 0x4000
    NEGATIVE_Z = NEGZ = 0x8000


class DDS:
    """DDS Header Structure."""

    HEADER = Header
    PF = PixelFormat
    CUBEMAP = 0x200
    CF = CubemapFlag
    CUBEMAPS = CUBEMAP | CF.POSX | CF.NEGX | CF.POSY | CF.NEGY | CF.POSZ | CF.NEGZ
    COMPLEX = 0x8
    TEXTURE = 0x1000
    MIPMAP = 0x400000
