"""Shared constants."""


class FormatSignature:
    """Binary format signatures."""

    MCSA = b"MCSA"
    MCAL = b"MCAL"
    MIC = b"\x89MIC"
    OL = b"\x0a\x95\x23\xfd"

    DDS = b"DDS "
    PNG = b"\x89PNG"
    GLTF = b"glTF"
    GZIP = b"\x1f\x8b"
    ZSTD = b"\x28\xb5\x2f\xfd"


class IntegerFactor:
    """Integer range limits."""

    I8 = 0x7F
    U8 = 0xFF
    I16 = 0x7FFF
    U16 = 0xFFFF
    I32 = 0x7FFFFFFF
    U32 = 0xFFFFFFFF
