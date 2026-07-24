"""
Collection of submodules that implement specific file format decoder/encoder.
"""

from . import (
    dae,
    dds,
    efkmodel,
    fbx,
    glb,
    hdri,
    json,
    mca,
    mcal,
    mcsa,
    mcsb,
    mdat,
    mic,
    ms3d,
    nbt,
    obj,
    ol,
    png,
    texarr,
    zip,
)
from .dae import DaeEncoder
from .dds import DdsEncoder
from .efkmodel import EfkmodelDecoder
from .fbx import FbxEncoder
from .glb import GlbEncoder
from .json import JsonEncoder
from .mca import McaEncoder
from .mcal import McalDecoder
from .mcsa import McsaDecoder
from .mcsb import McsbDecoder
from .mdat import MdatDecoder
from .mic import MicDecoder
from .ms3d import Ms3dEncoder
from .nbt import NbtDecoder
from .obj import ObjEncoder
from .ol import OlDecoder
from .png import PngEncoder
from .texarr import TexarrDecoder
from .zip import TexarrEncoder


__all__ = (
    "dae",
    "dds",
    "efkmodel",
    "fbx",
    "glb",
    "hdri",
    "json",
    "mca",
    "mcal",
    "mcsa",
    "mcsb",
    "mdat",
    "mic",
    "ms3d",
    "nbt",
    "obj",
    "ol",
    "png",
    "texarr",
    "zip",
    "DaeEncoder",
    "DdsEncoder",
    "EfkmodelDecoder",
    "FbxEncoder",
    "GlbEncoder",
    "JsonEncoder",
    "McaEncoder",
    "McalDecoder",
    "McsaDecoder",
    "McsbDecoder",
    "MdatDecoder",
    "MicDecoder",
    "Ms3dEncoder",
    "NbtDecoder",
    "ObjEncoder",
    "OlDecoder",
    "PngEncoder",
    "TexarrDecoder",
    "TexarrEncoder",
)
