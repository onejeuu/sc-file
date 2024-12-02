from .enums import FileFormat


SUPPORTED_FORMATS = {FileFormat.MCSA, FileFormat.MCVD, FileFormat.MIC, FileFormat.OL}
"""Files formats (suffixes without dot) that can be converted."""


class FileSignature:
    """File signature for formats (big-endian)."""

    MCSA = b"MCSA"
    MIC = b"\x89MIC"
    OL = b"\x0a\x95\x23\xfd"

    DDS = b"DDS "
    PNG = b"\x89PNG"
    FBX = b"Kaydara FBX Binary\x20\x20\x00\x1a\x00"
    GLTF = b"glTF"


class Factor:
    """Integer max range for integer type."""

    I8 = 0x7F
    U8 = 0xFF
    I16 = 0x7FFF
    U16 = 0xFFFF


class OlString:
    """Xor encoded zero-end string."""

    SIZE = 17
    """16 encoded bytes and last 0x00 byte."""
    XOR = ord("g")
    NULL = ord("G")


class CubemapFaces:
    """Dds cubemap faces."""

    FACES = {"+x", "-x", "+y", "-y", "+z", "-z"}
    COUNT = len(FACES)


class McsaModel:
    """Mcsa model constants."""

    ROUND_DIGITS = 6
    ROOT_BONE_ID = -1
    COUNT_LIMIT = 0x100000
    """There is no known limit. This for case when file was read incorrectly, so as not to overflow memory."""


class McsaSize:
    """Mcsa data structures elements count."""

    POSITION = 4
    TEXTURE = 2
    NORMALS = 4
    POLYGONS = 3
    COLOR = 4
    BONE = 3


class CLI:
    """Command line interface constants."""

    FORMATS = EPILOG = f"Supported Formats: {', '.join(sorted(SUPPORTED_FORMATS)).upper()}."
    VERSION = "4.0.0-dev"


class OutputFormats:
    """Supported output formats for file data types."""

    MODELS = {FileFormat.DAE, FileFormat.MS3D, FileFormat.MS3D_ASCII, FileFormat.OBJ}
    TEXTURES = {FileFormat.DDS}
    IMAGES = {FileFormat.PNG}
