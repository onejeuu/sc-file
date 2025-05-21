from .enums import CubemapFlag, HeaderFlag, PixelFormatFlag


class Header:
    SIZE = 124
    FLAG = HeaderFlag
    FLAGS = FLAG.CAPS | FLAG.HEIGHT | FLAG.WIDTH | FLAG.PIXELFORMAT | FLAG.MIPMAPCOUNT


class PixelFormat:
    SIZE = 32
    BIT_COUNT = 32
    FLAG = PixelFormatFlag
    RGB = FLAG.RGB | FLAG.ALPHAPIXELS


class DDS:
    HEADER = Header
    PF = PixelFormat
    CF = CubemapFlag
    CUBEMAP = 0x200
    CUBEMAPS = CUBEMAP | CF.POSX | CF.NEGX | CF.POSY | CF.NEGY | CF.POSZ | CF.NEGZ
    COMPLEX = 0x8
    TEXTURE = 0x1000
    MIPMAP = 0x400000
    CAPS1 = TEXTURE | COMPLEX | MIPMAP
