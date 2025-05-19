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


class PixelFormatFlag(IntFlag):
    ALPHAPIXELS = 0x1
    ALPHA = 0x2
    FOURCC = 0x4
    RGB = 0x40


class CubemapFlag(IntFlag):
    POSITIVE_X = POSX = 0x400
    NEGATIVE_X = NEGX = 0x800
    POSITIVE_Y = POSY = 0x1000
    NEGATIVE_Y = NEGY = 0x2000
    POSITIVE_Z = POSZ = 0x4000
    NEGATIVE_Z = NEGZ = 0x8000


class DXGIFormat(IntFlag):
    FLOAT_R32G32B32A32 = 2
    FLOAT_R32G32B32 = 6


class DXGIDimension(IntFlag):
    BUFFER = 1
    TEXTURE1D = 2
    TEXTURE2D = 3
    TEXTURE3D = 4
