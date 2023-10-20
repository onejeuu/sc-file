from typing import NamedTuple


class Signature(NamedTuple):
    MIC = 0x43494D89
    OL = 0xFD23950A
    MCSA = 0x4153434D


class Magic(NamedTuple):
    PNG = [0x89, 0x50, 0x4E, 0x47]
    DDS = [0x44, 0x44, 0x53, 0x20]


class Normalization(NamedTuple):
    BYTE = BONE_WEIGHT = 0xFF
    SHORT = VERTEX_LIMIT = 0x8000


class FileSuffix(NamedTuple):
    MIC = ".mic"
    OL = ".ol"
    MCSA = ".mcsa"
    PNG = ".png"
    DDS = ".dds"
    OBJ = ".obj"


# Model bone
ROOT_BONE_ID = -1
