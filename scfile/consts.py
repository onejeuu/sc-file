import os
from pathlib import Path
from typing import NamedTuple, TypeAlias

from .enums import FileSuffix


PathLike: TypeAlias = str | os.PathLike[str] | Path

class Signature(NamedTuple):
    """
    Little-Endian Source File Signature.
    Integer.
    """
    MIC = 0x43494D89
    OL = 0xFD23950A
    MCSA = 0x4153434D

class Magic(NamedTuple):
    """
    Little-Endian Output File Signature.
    List[Integer].
    """
    PNG = [0x89, 0x50, 0x4E, 0x47]
    DDS = [0x44, 0x44, 0x53, 0x20]

class Normalization(NamedTuple):
    # int range + 1
    I8 = VERTEX_WEIGHT = 0x80
    U8 = BONE_WEIGHT = 0x100
    I16 = XYZ_FACTOR = 0x8000
    U16 = WEIGHT_FACTOR = 0x10000

class OlString(NamedTuple):
    SIZE = 17 # 16 bytes + last 0x00 byte
    XOR = ord("g")
    NULL = ord("G")

class McsaModel(NamedTuple):
    ROOT_BONE_ID = -1
    # I dont know specific limit
    # This is done for case when file was read incorrectly
    # So as not to overflow memory
    COUNT_LIMIT = 0x40000

SUPPORTED_SUFFIXES = {FileSuffix.MIC, FileSuffix.OL, FileSuffix.MCSA}
