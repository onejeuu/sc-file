

type Format = bytes

SUPPORTED_FORMATS: list[Format] = [
    b"DXT1",
    b"DXT3",
    b"DXT5",
    b"RGBA8",
    b"BGRA8",
    b"RGBA32F",
    b"DXN_X",
    b"DXN_XY",
]
"""Supported texture pixel formats."""
