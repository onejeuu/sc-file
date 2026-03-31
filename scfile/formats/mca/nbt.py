import struct

from scfile.formats.nbt.enums import Tag


def encode(tag: int, name: bytes) -> bytes:
    return bytes([tag]) + struct.pack(">H", len(name)) + name


def compound(name: bytes, *children: bytes) -> bytes:
    return encode(Tag.COMPOUND, name) + b"".join(children) + b"\x00"


def lst(name: bytes, type: int, *v: bytes) -> bytes:
    return encode(Tag.LIST, name) + struct.pack(">bi", type, len(v)) + b"".join(v)


def encode_byte(name: bytes, v: int) -> bytes:
    return encode(Tag.BYTE, name) + struct.pack(">b", v)


def encode_int(name: bytes, v: int) -> bytes:
    return encode(Tag.INT, name) + struct.pack(">i", v)


def encode_long(name: bytes, v: int) -> bytes:
    return encode(Tag.LONG, name) + struct.pack(">q", v)


def encode_ba(name: bytes, v: bytes) -> bytes:
    return encode(Tag.BYTE_ARRAY, name) + struct.pack(">i", len(v)) + v


def encode_ia(name: bytes, arr: tuple[int, ...]) -> bytes:
    return encode(Tag.INT_ARRAY, name) + struct.pack(f">i{len(arr)}i", len(arr), *arr)
