from enum import IntFlag
from dataclasses import dataclass


class HeaderFlag(IntFlag):
    CAPS = 0x1
    HEIGHT = 0x2
    WIDTH = 0x4
    PITCH = 0x8
    PIXELFORMAT = 0x1000
    MIPMAPCOUNT = 0x20000
    LINEARSIZE = 0x80000
    DEPTH = 0x800000


@dataclass
class Header:
    SIZE = 124
    FLAG = HeaderFlag
    FLAGS = FLAG.CAPS | FLAG.HEIGHT | FLAG.WIDTH | FLAG.PIXELFORMAT | FLAG.MIPMAPCOUNT


@dataclass
class PixelFormatFlag(IntFlag):
    ALPHAPIXELS = 0x1
    ALPHA = 0x2
    FOURCC = 0x4
    RGB = 0x40


@dataclass
class PixelFormatBitmask:
    A = 0xFF000000
    R = 0x00FF0000
    G = 0x0000FF00
    B = 0x000000FF


@dataclass
class PixelFormat:
    SIZE = 32
    BIT_COUNT = 32
    BITMASK = PixelFormatBitmask()
    FLAG = PixelFormatFlag
    RGB_FLAGS = FLAG.RGB | FLAG.ALPHAPIXELS


class DDS:
    HEADER = Header()
    PF = PixelFormat()
    COMPLEX = 0x8
    TEXTURE = 0x1000
    MIPMAP = 0x400000
