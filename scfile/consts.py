from .enums import FileSuffix


class Signature:
    """
    Big-Endian Source File Signature.
    Integer.
    """

    MCSA = 0x4D435341
    MIC = 0x894D4943
    OL = 0x0A9523FD


class Magic:
    """
    Big-Endian Output File Signature.
    List[Integer].
    """

    DDS = [0x44, 0x44, 0x53, 0x20]
    PNG = [0x89, 0x50, 0x4E, 0x47]


class Factor:
    """
    Integer range.
    """

    I8 = 0x7F
    U8 = 0xFF
    I16 = 0x7FFF
    U16 = 0xFFFF


class OlString:
    """
    Xor encoded zero-end string.
    """

    SIZE = 17
    """16 encoded bytes and last 0x00 byte."""
    XOR = ord("g")
    NULL = ord("G")


class McsaModel:
    """
    Mcsa model constants.
    """

    ROOT_BONE_ID = -1
    COUNT_LIMIT = 0x100000
    """There is no known limit. This for case when file was read incorrectly, so as not to overflow memory."""


class McsaSize:
    """
    Count of elements in each mcsa data structure.
    """

    POSITION = 4
    TEXTURE = 2
    NORMALS = 4
    POLYGONS = 3
    COLOR = 4


SUPPORTED_SUFFIXES = {FileSuffix.MCSA, FileSuffix.MCVD, FileSuffix.MIC, FileSuffix.OL}
"""Files suffixes that can be converted."""


CUBEMAP_FACES = 6
"""Dds cubemap faces count. (+x, -x, +y, -y, +z, -z)."""
