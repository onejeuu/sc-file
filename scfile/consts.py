from .enums import FileSuffix


class Signature:
    """
    Little-Endian Source File Signature.
    Integer.
    """

    MIC = 0x43494D89
    OL = 0xFD23950A
    MCSA = 0x4153434D


class Magic:
    """
    Little-Endian Output File Signature.
    List[Integer].
    """

    PNG = [0x89, 0x50, 0x4E, 0x47]
    DDS = [0x44, 0x44, 0x53, 0x20]


class Factor:
    # int range + 1
    I8 = NORMALS = 0x80
    U8 = BONE_WEIGHT = 0x100
    I16 = XYZ = UV = 0x8000
    U16 = 0x10000


class OlString:
    SIZE = 17  # 16 bytes + last 0x00 byte
    XOR = ord("g")
    NULL = ord("G")


class McsaModel:
    ROOT_BONE_ID = -1
    # I dont know specific limit
    # This is done for case when file was read incorrectly
    # So as not to overflow memory
    COUNT_LIMIT = 0x40000


class McsaSize:
    # Number of elements in each structure
    POSITION = 4
    TEXTURE = 2
    NORMALS = 4
    POLYGONS = 3


# Files suffixes that can be converted
SUPPORTED_SUFFIXES = {FileSuffix.MIC, FileSuffix.OL, FileSuffix.MCSA}

# Dds cubemap faces count
# +x, -x, +y, -y, +z, -z
CUBEMAP_FACES = 6
