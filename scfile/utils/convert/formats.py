from functools import partial

from scfile.formats.dae.encoder import DaeEncoder
from scfile.formats.dds.encoder import DdsEncoder
from scfile.formats.glb.encoder import GlbEncoder
from scfile.formats.mcsa.decoder import McsaDecoder
from scfile.formats.mic.decoder import MicDecoder
from scfile.formats.ms3d.encoder import Ms3dEncoder
from scfile.formats.obj.encoder import ObjEncoder
from scfile.formats.ol.decoder import OlDecoder
from scfile.formats.png.encoder import PngEncoder

from .base import convert


# TODO: try to get annotations cast

mcsa_to_dae = partial(
    convert,
    decoder=McsaDecoder,
    encoder=DaeEncoder,
)

mcsa_to_obj = partial(
    convert,
    decoder=McsaDecoder,
    encoder=ObjEncoder,
)

mcsa_to_gltf = partial(
    convert,
    decoder=McsaDecoder,
    encoder=GlbEncoder,
)

mcsa_to_ms3d = partial(
    convert,
    decoder=McsaDecoder,
    encoder=Ms3dEncoder,
)

ol_to_dds = partial(
    convert,
    decoder=OlDecoder,
    encoder=DdsEncoder,
)

mic_to_png = partial(
    convert,
    decoder=MicDecoder,
    encoder=PngEncoder,
)
