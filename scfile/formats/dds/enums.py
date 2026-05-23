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
    FLOAT_R32G32B32A32 = 0x2
    FLOAT_R32G32B32 = 0x6


class DXGIDimension(IntFlag):
    BUFFER = 0x1
    TEXTURE1D = 0x2
    TEXTURE2D = 0x3
    TEXTURE3D = 0x4


class ChannelMask(IntFlag):
    RED = R = 0x000000FF
    GREEN = G = 0x0000FF00
    BLUE = B = 0x00FF0000
    ALPHA = A = 0xFF000000


RGBA8 = (ChannelMask.R, ChannelMask.G, ChannelMask.B, ChannelMask.A)
BGRA8 = (ChannelMask.B, ChannelMask.G, ChannelMask.R, ChannelMask.A)
