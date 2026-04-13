from copy import deepcopy

import click
import numpy as np

from scfile import exceptions, formats
from scfile.cli import types, version
from scfile.core.context.options import UserOptions
from scfile.enums import CliCommand, FileFormat
from scfile.structures.mesh import ModelMesh
from scfile.structures.scene import ModelScene

from . import scfile


WHITELIST: set[FileFormat] = {FileFormat.MCSA, FileFormat.MCSB, FileFormat.MCVD}
SUFFIXES: set[str] = set(map(lambda fmt: fmt.suffix, WHITELIST))


def _build_bone_name_index(scene) -> dict[str, int]:
    return {str(b.name): int(i) for i, b in enumerate(scene.skeleton.bones)}


def _normalize_bone_name(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


def _resolve_target_bone_index(src_name: str, target_bones_by_name: dict[str, int]) -> int | None:
    direct = target_bones_by_name.get(src_name)
    if direct is not None:
        return int(direct)

    normalized_target = {_normalize_bone_name(k): v for k, v in target_bones_by_name.items()}
    src_norm = _normalize_bone_name(src_name)
    norm_hit = normalized_target.get(src_norm)
    if norm_hit is not None:
        return int(norm_hit)

    # Common technical tails: *_end / .end / _nub.
    base = src_name
    for suffix in ("_end", ".end", "_nub", ".nub"):
        if base.lower().endswith(suffix):
            base = base[: -len(suffix)]
            break

    if base != src_name:
        direct_base = target_bones_by_name.get(base)
        if direct_base is not None:
            return int(direct_base)
        base_norm = _normalize_bone_name(base)
        norm_base = normalized_target.get(base_norm)
        if norm_base is not None:
            return int(norm_base)

    return None


def _resolve_target_from_source_chain(source_bones, src_idx: int, target_bones_by_name: dict[str, int]) -> int | None:
    idx = int(src_idx)
    while 0 <= idx < len(source_bones):
        name = str(source_bones[idx].name)
        hit = _resolve_target_bone_index(name, target_bones_by_name)
        if hit is not None:
            return int(hit)
        idx = int(source_bones[idx].parent_id)
    return None


def _remap_skeleton(mesh: ModelMesh, source_scene: ModelScene, target_scene: ModelScene) -> ModelMesh:
    m = deepcopy(mesh)

    if m.links_ids.size == 0 or m.links_weights.size == 0:
        return m

    source_bones = source_scene.skeleton.bones
    target_bones_by_name = _build_bone_name_index(target_scene)

    # Map each source skeleton bone id to a target skeleton bone id.
    src_id_to_target: dict[int, int] = {}
    for src_idx, _src_bone in enumerate(source_bones):
        target_idx = _resolve_target_from_source_chain(
            source_bones=source_bones,
            src_idx=src_idx,
            target_bones_by_name=target_bones_by_name,
        )
        if target_idx is not None:
            src_id_to_target[int(src_idx)] = int(target_idx)

    ids = m.links_ids.astype(np.int32).copy()
    weights = m.links_weights.astype(np.float32).copy()
    out_ids = np.zeros_like(ids, dtype=np.uint8)
    matched = np.zeros_like(ids, dtype=bool)

    for src_id, target_idx in src_id_to_target.items():
        mask = ids == int(src_id)
        out_ids[mask] = np.uint8(target_idx)
        matched[mask] = True

    # Keep only mapped influences.
    weights[~matched] = 0.0

    # Normalize per vertex.
    sums = weights.sum(axis=1, keepdims=True)
    non_zero = sums[:, 0] > 1e-8
    if np.any(non_zero):
        weights[non_zero] /= sums[non_zero]

    # If a vertex lost all mapped influence, pin to wpn_body.
    zero_vertices = ~non_zero
    if np.any(zero_vertices):
        fallback_idx = int(target_bones_by_name.get("wpn_body", 0))
        out_ids[zero_vertices, :] = 0
        out_ids[zero_vertices, 0] = np.uint8(fallback_idx)
        weights[zero_vertices, :] = 0.0
        weights[zero_vertices, 0] = 1.0

    out_ids[weights <= 0.0] = 0

    m.links_ids = out_ids.astype(np.uint8)
    m.links_weights = weights.astype(np.float32)
    return m


@scfile.command(name=CliCommand.RETARGET)
@click.argument(
    "HANDS",
    type=types.RetargetPath,
    nargs=1,
)
@click.argument(
    "WEAPON",
    type=types.RetargetPath,
    nargs=1,
)
@click.argument(
    "FPANIM",
    type=types.RetargetPath,
    nargs=1,
)
@click.option(
    "--version",
    help="Show the version and exit.",
    callback=version.callback,
    is_flag=True,
    is_eager=True,
    expose_value=False,
)
def retarget_command(
    hands: types.PathType,
    weapon: types.PathType,
    fpanim: types.PathType,
) -> None:
    for path in (hands, weapon, fpanim):
        if path.suffix not in SUFFIXES:
            raise exceptions.UnsupportedFormatError(path)

    options = UserOptions(parse_skeleton=True, parse_animation=True)

    with formats.mcsb.McsbDecoder(hands, options) as mcsb:
        hands_scene = mcsb.decode().scene

    with formats.mcsb.McsbDecoder(weapon, options) as mcsb:
        weapon_scene = mcsb.decode().scene

    with formats.mcsa.McsaDecoder(fpanim, options) as mcsa:
        anims_data = mcsa.decode()

    output = deepcopy(anims_data)
    output.scene.meshes = []

    for mesh in hands_scene.meshes:
        output.scene.meshes.append(
            _remap_skeleton(
                mesh=mesh,
                source_scene=hands_scene,
                target_scene=output.scene,
            )
        )

    for mesh in weapon_scene.meshes:
        output.scene.meshes.append(
            _remap_skeleton(
                mesh=mesh,
                source_scene=weapon_scene,
                target_scene=output.scene,
            )
        )

    output.scene.count.meshes = len(output.scene.meshes)

    with formats.glb.GlbEncoder(output, options) as glb:
        glb.encode()
        glb.export("F:/tmp/test")
