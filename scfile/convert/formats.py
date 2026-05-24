"""
Named conversion functions for specific format pairs.
"""

from typing import Optional

from scfile import formats
from scfile.core import Options
from scfile.types import PathLike

from .factory import converter


@converter(formats.mcsb.McsbDecoder, formats.obj.ObjEncoder)
def mcsb_to_obj(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.mcsb`` to ``.obj`` format.

    Arguments:
        source: Path to source ``.mcsb`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``mcsb_to_obj("model.mcsb", "model.obj")``
    """


@converter(formats.mcsb.McsbDecoder, formats.glb.GlbEncoder)
def mcsb_to_glb(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.mcsb`` to ``.glb`` format.

    Arguments:
        source: Path to source ``.mcsb`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``mcsb_to_glb("model.mcsb", "model.glb")``
    """


@converter(formats.mcsb.McsbDecoder, formats.dae.DaeEncoder)
def mcsb_to_dae(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.mcsb`` to ``.dae`` format.

    Arguments:
        source: Path to source ``.mcsb`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``mcsb_to_dae("model.mcsb", "model.dae")``
    """


@converter(formats.mcsb.McsbDecoder, formats.ms3d.Ms3dEncoder)
def mcsb_to_ms3d(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.mcsb`` to ``.ms3d`` format.

    Arguments:
        source: Path to source ``.mcsb`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``mcsb_to_ms3d("model.mcsb", "model.ms3d")``
    """


@converter(formats.mcsb.McsbDecoder, formats.fbx.FbxEncoder)
def mcsb_to_fbx(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.mcsb`` to ``.fbx`` format.

    Arguments:
        source: Path to source ``.mcsb`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``mcsb_to_fbx("model.mcsb", "model.fbx")``
    """


@converter(formats.mcsa.McsaDecoder, formats.obj.ObjEncoder)
def mcsa_to_obj(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.mcsa`` to ``.obj`` format.

    Arguments:
        source: Path to source ``.mcsa`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``mcsa_to_obj("model.mcsa", "model.obj")``
    """


@converter(formats.mcsa.McsaDecoder, formats.glb.GlbEncoder)
def mcsa_to_glb(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.mcsa`` to ``.glb`` format.

    Arguments:
        source: Path to source ``.mcsa`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``mcsa_to_glb("model.mcsa", "model.glb")``
    """


@converter(formats.mcsa.McsaDecoder, formats.dae.DaeEncoder)
def mcsa_to_dae(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.mcsa`` to ``.dae`` format.

    Arguments:
        source: Path to source ``.mcsa`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``mcsa_to_dae("model.mcsa", "model.dae")``
    """


@converter(formats.mcsa.McsaDecoder, formats.ms3d.Ms3dEncoder)
def mcsa_to_ms3d(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.mcsa`` to ``.ms3d`` format.

    Arguments:
        source: Path to source ``.mcsa`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``mcsa_to_ms3d("model.mcsa", "model.ms3d")``
    """


@converter(formats.mcsa.McsaDecoder, formats.fbx.FbxEncoder)
def mcsa_to_fbx(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.mcsa`` to ``.fbx`` format.

    Arguments:
        source: Path to source ``.mcsa`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``mcsa_to_fbx("model.mcsa", "model.fbx")``
    """


@converter(formats.efkmodel.EfkmodelDecoder, formats.obj.ObjEncoder)
def efkmodel_to_obj(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.efkmodel`` to ``.obj`` format.

    Arguments:
        source: Path to source ``.efkmodel`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``efkmodel_to_obj("model.efkmodel", "model.obj")``
    """


@converter(formats.efkmodel.EfkmodelDecoder, formats.glb.GlbEncoder)
def efkmodel_to_glb(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.efkmodel`` to ``.glb`` format.

    Arguments:
        source: Path to source ``.efkmodel`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``efkmodel_to_glb("model.efkmodel", "model.glb")``
    """


@converter(formats.efkmodel.EfkmodelDecoder, formats.dae.DaeEncoder)
def efkmodel_to_dae(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.efkmodel`` to ``.dae`` format.

    Arguments:
        source: Path to source ``.efkmodel`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``efkmodel_to_dae("model.efkmodel", "model.dae")``
    """


@converter(formats.efkmodel.EfkmodelDecoder, formats.ms3d.Ms3dEncoder)
def efkmodel_to_ms3d(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.efkmodel`` to ``.ms3d`` format.

    Arguments:
        source: Path to source ``.efkmodel`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``efkmodel_to_ms3d("model.efkmodel", "model.ms3d")``
    """


@converter(formats.efkmodel.EfkmodelDecoder, formats.fbx.FbxEncoder)
def efkmodel_to_fbx(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts model from ``.efkmodel`` to ``.fbx`` format.

    Arguments:
        source: Path to source ``.efkmodel`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``efkmodel_to_fbx("model.efkmodel", "model.fbx")``
    """


@converter(formats.ol.OlDecoder, formats.dds.DdsEncoder)
def ol_to_dds(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts texture from ``.ol`` to ``.dds`` format.

    Arguments:
        source: Path to source ``.ol`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``ol_to_dds("texture.ol", "texture.dds")``
    """


@converter(formats.hdri.OlCubemapDecoder, formats.dds.DdsEncoder)
def ol_cubemap_to_dds(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts cubemap texture from ``.ol`` to ``.dds`` format.

    Arguments:
        source: Path to source ``.ol`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``ol_cubemap_to_dds("cubemap.ol", "cubemap.dds")``
    """


@converter(formats.mic.MicDecoder, formats.png.PngEncoder)
def mic_to_png(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts image from ``.mic`` to ``.png`` format.

    Arguments:
        source: Path to source ``.mic`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``mic_to_png("image.mic", "image.png")``
    """


@converter(formats.texarr.TexarrDecoder, formats.zip.TexarrEncoder)
def texarr_to_zip(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts texture array from ``.texarr`` to ``.zip`` format.

    Arguments:
        source: Path to source ``.texarr`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``texarr_to_zip("blocks.texarr", "blocks.zip")``
    """


@converter(formats.nbt.NbtDecoder, formats.json.JsonEncoder)
def nbt_to_json(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts data from ``NBT`` to ``.json`` format.

    Arguments:
        source: Path to source ``NBT`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``nbt_to_json("itemnames.dat", "itemnames.json")``
    """


@converter(formats.mdat.MdatDecoder, formats.mca.McaEncoder)
def mdat_to_mca(
    source: PathLike,
    output: Optional[PathLike] = None,
    options: Optional[Options] = None,
):
    """
    Converts world region from ``.mdat`` to ``.mca`` format.

    Arguments:
        source: Path to source ``.mdat`` file.
        output (optional): Path to output directory. Defaults: ``Same directory as source``.
        options (optional): User settings. Default: ``None``.

    Example:
        ``mdat_to_mca("reg.0.0.mdat", "r.0.0.mca")``
    """
