"""Supported MDAT versions and their binary layouts."""

from struct import Struct


type Version = int

SUPPORTED_VERSIONS: tuple[Version, ...] = (5, 6, 7)

REGION_KEY_BYTES: dict[Version, int] = {
    5: 16,
    6: 16,
    7: 8,
}

CHUNK_HEADERS: dict[Version, Struct] = {
    5: Struct(">5i"),
    6: Struct(">5i"),
    7: Struct(">i8s4i"),
}
