from .enums import FileFormat
from .types import Formats


SUPPORTED_FORMATS: set[FileFormat] = {
    FileFormat.EFKMODEL,
    FileFormat.MCSA,
    FileFormat.MCSB,
    FileFormat.MCVD,
    FileFormat.MIC,
    FileFormat.OL,
    FileFormat.TEXARR,
    FileFormat.NBT,
    FileFormat.MDAT,
}
"""Formats available for conversion."""

SUPPORTED_SUFFIXES: set[str] = set(map(lambda fmt: fmt.suffix, SUPPORTED_FORMATS))
"""Formats suffixes available for conversion."""

SUPPORTED_NBT: set[str] = {"itemnames.dat", "prefs", "common", "sd0", "sd1", "sd2", "sd3", "sd4"}
"""NBT filenames available for conversion."""

ALLOWED_SUFFIXES: set[str] = SUPPORTED_SUFFIXES | SUPPORTED_NBT
"""All path suffixes available for conversion."""


class FileSignature:
    """Format magic bytes."""

    MCSA = b"MCSA"
    MCAL = b"MCAL"
    MIC = b"\x89MIC"
    OL = b"\x0a\x95\x23\xfd"

    DDS = b"DDS "
    PNG = b"\x89PNG"
    GLTF = b"glTF"
    MS3D = b"MS3D000000"


class CLI:
    """Command line interface constants."""

    NON_SKELETAL_FORMATS: Formats = (FileFormat.OBJ, FileFormat.FBX)
    NON_ANIMATION_FORMATS: Formats = (FileFormat.OBJ, FileFormat.FBX, FileFormat.DAE, FileFormat.MS3D)


class OutputFormats:
    """Supported output formats for file data types."""

    MODELS: Formats = (FileFormat.OBJ, FileFormat.GLB, FileFormat.FBX, FileFormat.DAE, FileFormat.MS3D)
    TEXTURES: Formats = (FileFormat.DDS,)
    IMAGES: Formats = (FileFormat.PNG,)
    REGIONS: Formats = (FileFormat.MCA,)
    TEXARR: Formats = (FileFormat.ZIP,)
    NBT: Formats = (FileFormat.NBT,)


class DefaultModelFormats:
    """Default model formats for unset options."""

    STANDARD: Formats = (FileFormat.OBJ,)
    ON_SKELETON: Formats = (FileFormat.GLB,)


class Factor:
    """Integer range limits."""

    I8 = 0x7F
    U8 = 0xFF
    I16 = 0x7FFF
    U16 = 0xFFFF
    I32 = 0x7FFFFFFF
    U32 = 0xFFFFFFFF


class CubemapFaces:
    """DDS cubemap faces."""

    FACES = {"+x", "-x", "+y", "-y", "+z", "-z"}
    COUNT = len(FACES)


class ModelDefaults:
    """Model default constants."""

    DECIMALS = 6
    ROOT_BONE_ID = -1
    GEOMETRY_LIMIT = 1_000_000
    """Safety limit to prevent memory overflow on corrupted files."""


class Text:
    """Shared text constants."""

    FORMATS = f"Supported Formats: {sorted(SUPPORTED_SUFFIXES)}"
    NBT = f"Supported NBTs: {sorted(SUPPORTED_NBT)}"
    EXCEPTION = "[b yellow]Input file appears to be corrupted or invalid.[/]"
