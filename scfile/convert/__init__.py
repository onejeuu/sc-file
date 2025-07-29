"""
Utility module. Handles conversion logic between formats.
"""

from . import base, legacy, detect, formats
from .detect import auto
from .formats import (
    mcsb_to_dae,
    mcsb_to_glb,
    mcsb_to_ms3d,
    mcsb_to_obj,
    ol_to_dds,
    ol_cubemap_to_dds,
    mic_to_png,
    texarr_to_zip,
)


__all__ = (
    "base",
    "legacy",
    "detect",
    "formats",
    "auto",
    "mcsb_to_dae",
    "mcsb_to_glb",
    "mcsb_to_ms3d",
    "mcsb_to_obj",
    "ol_to_dds",
    "ol_cubemap_to_dds",
    "mic_to_png",
    "texarr_to_zip",
)
