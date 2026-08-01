from .enums import FileFormat


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

INVALID_INPUT_HINT = "Input file appears to be corrupted or invalid."
"""Hint shown when binary parsing suggests invalid input."""


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


class IntegerFactor:
    """Integer range limits."""

    I8 = 0x7F
    U8 = 0xFF
    I16 = 0x7FFF
    U16 = 0xFFFF
    I32 = 0x7FFFFFFF
    U32 = 0xFFFFFFFF
