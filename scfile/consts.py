from .enums import FileFormat


SUPPORTED_FORMATS: set[FileFormat] = {FileFormat.MCSA, FileFormat.MCSB, FileFormat.MCVD, FileFormat.MIC, FileFormat.OL}
"""Files formats (suffixes without dot) that can be converted."""

SUPPORTED_SUFFIXES: set[str] = set(map(lambda fmt: f".{fmt}", SUPPORTED_FORMATS))
"""Files suffixes that can be converted."""


class FileSignature:
    """File signature for formats (big-endian)."""

    MCSA = b"MCSA"
    MIC = b"\x89MIC"
    OL = b"\x0a\x95\x23\xfd"

    DDS = b"DDS "
    PNG = b"\x89PNG"
    FBX = b"Kaydara FBX Binary\x20\x20\x00\x1a\x00"
    GLTF = b"glTF"
    MS3D = b"MS3D000000"


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
    DEFAULTS = 3
    CLIP_FRAMES = 7


class CLI:
    """Command line interface constants."""

    VERSION = "4.0.0.dev"
    FORMATS = EPILOG = f"Supported formats: {', '.join(sorted(SUPPORTED_SUFFIXES))}"
    PAUSE_TEXT = "\nPress Enter to continue or exit..."

    class Text:
        INVALID_FILE = "input file is invalid or corrupted"
        EXCEPTION = f"[b yellow]This usually means {INVALID_FILE}.[/]"
        HDRI_ON = f"[b yellow]This file is most likely skybox hdri cubemap texture. Try specifying --hdri flag. Otherwise, most likely {INVALID_FILE}.[/]"
        HDRI_OFF = f"[b yellow]This file is most likely IS NOT skybox hdri cubemap texture. Try remove --hdri flag. Otherwise, most likely {INVALID_FILE}.[/]"


class OutputFormats:
    """Supported output formats for file data types."""

    MODELS = sorted({FileFormat.DAE, FileFormat.MS3D, FileFormat.OBJ, FileFormat.GLB})
    TEXTURES = sorted({FileFormat.DDS})
    IMAGES = sorted({FileFormat.PNG})
