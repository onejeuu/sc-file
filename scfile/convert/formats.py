from functools import wraps
from typing import Callable, Optional, Type

from scfile.convert.base import convert
from scfile.core import FileDecoder, FileEncoder
from scfile.core.context import ImageOptions, ModelOptions, TextureOptions
from scfile.core.types import Content, Options, PathLike
from scfile.formats.dae.encoder import DaeEncoder
from scfile.formats.dds.encoder import DdsEncoder
from scfile.formats.glb.encoder import GlbEncoder
from scfile.formats.mcsa.decoder import McsaDecoder
from scfile.formats.mcsb.decoder import McsbDecoder
from scfile.formats.mic.decoder import MicDecoder
from scfile.formats.ms3d.encoder import Ms3dEncoder
from scfile.formats.obj.encoder import ObjEncoder
from scfile.formats.ol.decoder import OlDecoder
from scfile.formats.png.encoder import PngEncoder


def converter(
    decoder: Type[FileDecoder[Content, Options]],
    encoder: Type[FileEncoder[Content, Options]],
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(
            source: PathLike,
            output: Optional[PathLike] = None,
            options: Optional[Options] = None,
            overwrite: bool = True,
        ) -> None:
            convert(
                decoder=decoder,
                encoder=encoder,
                source=source,
                output=output,
                options=options,
                overwrite=overwrite,
            )

        return wrapper

    return decorator


@converter(McsbDecoder, DaeEncoder)
def mcsb_to_dae(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[ModelOptions] = None,
    overwrite: bool = True,
):
    pass


@converter(McsbDecoder, ObjEncoder)
def mcsb_to_obj(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[ModelOptions] = None,
    overwrite: bool = True,
):
    pass


@converter(McsbDecoder, GlbEncoder)
def mcsb_to_gltf(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[ModelOptions] = None,
    overwrite: bool = True,
):
    pass


@converter(McsbDecoder, Ms3dEncoder)
def mcsb_to_ms3d(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[ModelOptions] = None,
    overwrite: bool = True,
):
    pass


@converter(OlDecoder, DdsEncoder)
def ol_to_dds(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[TextureOptions] = None,
    overwrite: bool = True,
):
    pass


@converter(MicDecoder, PngEncoder)
def mic_to_png(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[ImageOptions] = None,
    overwrite: bool = True,
):
    pass


# ? Legacy
@converter(McsaDecoder, DaeEncoder)
def mcsa_to_dae(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[ModelOptions] = None,
    overwrite: bool = True,
):
    pass


@converter(McsaDecoder, ObjEncoder)
def mcsa_to_obj(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[ModelOptions] = None,
    overwrite: bool = True,
):
    pass


@converter(McsaDecoder, GlbEncoder)
def mcsa_to_gltf(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[ModelOptions] = None,
    overwrite: bool = True,
):
    pass


@converter(McsaDecoder, Ms3dEncoder)
def mcsa_to_ms3d(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[ModelOptions] = None,
    overwrite: bool = True,
):
    pass
