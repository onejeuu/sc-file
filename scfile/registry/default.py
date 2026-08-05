"""
Built-in file formats registry.
"""

from scfile import formats

from .registry import Registry
from .resolver import Resolver


REGISTRY = Registry(
    formats.DaeEncoder,
    formats.DdsEncoder,
    formats.EfkmodelDecoder,
    formats.FbxEncoder,
    formats.GlbEncoder,
    formats.JsonEncoder,
    formats.McaEncoder,
    formats.McalDecoder,
    formats.McsaDecoder,
    formats.McsbDecoder,
    formats.McvdDecoder,
    formats.MdatDecoder,
    formats.MicDecoder,
    formats.Ms3dEncoder,
    formats.NbtDecoder,
    formats.ObjEncoder,
    formats.OlDecoder,
    formats.PngEncoder,
    formats.TexarrDecoder,
    formats.ZipEncoder,
)

RESOLVER = Resolver(REGISTRY)
