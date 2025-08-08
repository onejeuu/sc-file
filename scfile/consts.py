from typing import Sequence, TypeAlias

from .enums import FileFormat


Formats: TypeAlias = Sequence[FileFormat]


SUPPORTED_FORMATS: set[FileFormat] = {
    FileFormat.MCSA,
    FileFormat.MCSB,
    FileFormat.MCVD,
    FileFormat.MIC,
    FileFormat.OL,
    FileFormat.TEXARR,
}
"""Files formats (suffixes without dot) that can be converted."""

SUPPORTED_SUFFIXES: set[str] = set(map(lambda fmt: fmt.suffix, SUPPORTED_FORMATS))
"""Files suffixes that can be converted."""


class FileSignature:
    """File magic number for formats (big-endian)."""

    MCSA = b"MCSA"
    MCAL = b"MCAL"
    MIC = b"\x89MIC"
    OL = b"\x0a\x95\x23\xfd"

    DDS = b"DDS "
    PNG = b"\x89PNG"
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

    DECIMALS = 6
    ROOT_BONE_ID = -1
    GEOMETRY_LIMIT = 1_000_000
    """Safety limit to prevent memory overflow on corrupted files."""


class McsaUnits:
    """Mcsa structures elements count."""

    POSITIONS = 4
    TEXTURES = 2
    NORMALS = 4
    POLYGONS = 3
    LINKS = 4
    BONES = 6
    FRAMES = 7


class CLI:
    """Command line interface constants."""

    VERSION = "4.1.1"

    FORMATS = EPILOG = f"Supported formats: {', '.join(sorted(SUPPORTED_SUFFIXES))}"
    PAUSE = "\nPress any key to continue or exit..."
    EXCEPTION = "[b yellow]Input file appears to be corrupted or invalid.[/]"

    NON_SKELETAL_FORMATS: Formats = (FileFormat.OBJ,)
    NON_ANIMATION_FORMATS: Formats = (FileFormat.OBJ, FileFormat.MS3D, FileFormat.DAE)


class OutputFormats:
    """Supported output formats for file data types."""

    MODELS: Formats = (FileFormat.OBJ, FileFormat.GLB, FileFormat.DAE, FileFormat.MS3D)
    TEXTURES: Formats = (FileFormat.DDS,)
    IMAGES: Formats = (FileFormat.PNG,)


class DefaultModelFormats:
    """Default model formats for cases where no preference is specified."""

    STANDARD: Formats = (FileFormat.OBJ,)
    SKELETON: Formats = (FileFormat.GLB,)
