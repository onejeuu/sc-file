"""Format handlers catalog."""

from . import (
    dds,
    efkmodel,
    fbx,
    glb,
    json,
    mca,
    mcal,
    mcsa,
    mcsb,
    mcvd,
    mdat,
    mic,
    nbt,
    obj,
    ol,
    png,
    texarr,
    zip,
)
from .dds import DdsEncoder
from .efkmodel import EfkmodelDecoder
from .fbx import FbxEncoder
from .glb import GlbEncoder
from .json import JsonEncoder
from .mca import McaEncoder
from .mcal import McalDecoder
from .mcsa import McsaDecoder
from .mcsb import McsbDecoder
from .mcvd import McvdDecoder
from .mdat import MdatDecoder
from .mic import MicDecoder
from .nbt import NbtDecoder
from .obj import ObjEncoder
from .ol import OlDecoder
from .png import PngEncoder
from .texarr import TexarrDecoder
from .zip import ZipEncoder
from .registry import Registry

from scfile.enums import FileFormat


registry = Registry(
    decoders=(
        EfkmodelDecoder,
        McalDecoder,
        McsaDecoder,
        McsbDecoder,
        McvdDecoder,
        MdatDecoder,
        MicDecoder,
        NbtDecoder,
        OlDecoder,
        TexarrDecoder,
    ),
    encoders=(
        DdsEncoder,
        FbxEncoder,
        GlbEncoder,
        JsonEncoder,
        McaEncoder,
        ObjEncoder,
        PngEncoder,
        ZipEncoder,
    ),
    aliases={FileFormat.NBT: nbt.SUPPORTED_FILENAMES},
)


__all__ = (
    "dds",
    "efkmodel",
    "fbx",
    "glb",
    "json",
    "mca",
    "mcal",
    "mcsa",
    "mcsb",
    "mcvd",
    "mdat",
    "mic",
    "nbt",
    "obj",
    "ol",
    "png",
    "texarr",
    "zip",
    "DdsEncoder",
    "EfkmodelDecoder",
    "FbxEncoder",
    "GlbEncoder",
    "JsonEncoder",
    "McaEncoder",
    "McalDecoder",
    "McsaDecoder",
    "McsbDecoder",
    "McvdDecoder",
    "MdatDecoder",
    "MicDecoder",
    "NbtDecoder",
    "ObjEncoder",
    "OlDecoder",
    "PngEncoder",
    "TexarrDecoder",
    "ZipEncoder",
    "registry",
)
