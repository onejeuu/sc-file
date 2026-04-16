"""
Co-author: [TeamDima](https://github.com/DeTTK)
"""

from copy import deepcopy

import click
import numpy as np

from scfile import exceptions, formats
from scfile.cli import types, version
from scfile.core.context.options import UserOptions
from scfile.enums import CliCommand, FileFormat
from scfile.structures.mesh import ModelMesh
from scfile.structures.scene import ModelScene
from scfile.structures.skeleton import SkeletonBone, create_transform_matrix

from . import scfile


WHITELIST: set[FileFormat] = {FileFormat.MCSA, FileFormat.MCSB, FileFormat.MCVD}
SUFFIXES: set[str] = set(map(lambda fmt: fmt.suffix, WHITELIST))

BONE_ALIASES = {
    "armr": ["RightHand", "RightForeArm", "RightArm"],
    "arml": ["LeftHand", "LeftForeArm", "LeftArm"],
    "forearmr": ["RightForeArm", "RightArm"],
    "forearml": ["LeftForeArm", "LeftArm"],
    "handr": ["RightHand", "RightForeArm", "RightArm"],
    "handl": ["LeftHand", "LeftForeArm", "LeftArm"],
    "rarm": ["RightHand", "RightForeArm", "RightArm"],
    "larm": ["LeftHand", "LeftForeArm", "LeftArm"],
    "rhand": ["RightHand", "RightForeArm", "RightArm"],
    "lhand": ["LeftHand", "LeftForeArm", "LeftArm"],
}


def _calc_global_mats(scene: ModelScene) -> list[np.ndarray]:
    mats = []
    for bone in scene.skeleton.bones:
        local = create_transform_matrix(bone.position, bone.rotation)
        if int(bone.parent_id) < 0:
            mats.append(local)
        else:
            mats.append(mats[int(bone.parent_id)] @ local)
    return mats


def _build_bone_name_index(scene) -> dict[str, int]:
    return {str(b.name): int(i) for i, b in enumerate(scene.skeleton.bones)}


def _resolve_target_bone_index(src_name: str, target_bones_by_name: dict[str, int]) -> int | None:
    if src_name in target_bones_by_name:
        return target_bones_by_name[src_name]

    norm_name = "".join(ch for ch in src_name.lower() if ch.isalnum())
    if norm_name in BONE_ALIASES:
        for alias in BONE_ALIASES[norm_name]:
            if alias in target_bones_by_name:
                return target_bones_by_name[alias]

    normalized_target = {"".join(ch for ch in k.lower() if ch.isalnum()): v for k, v in target_bones_by_name.items()}
    return normalized_target.get(norm_name)


def _resolve_target_from_source_chain(
    source_bones: list[SkeletonBone],
    src_idx: int,
    target_bones_by_name: dict[str, int],
) -> int | None:
    idx = int(src_idx)
    while 0 <= idx < len(source_bones):
        name = str(source_bones[idx].name)
        hit = _resolve_target_bone_index(name, target_bones_by_name)
        if hit is not None:
            return int(hit)
        idx = int(source_bones[idx].parent_id)
    return None


def _remap_skeleton(
    mesh: ModelMesh,
    source_scene: ModelScene,
    target_scene: ModelScene,
    is_weapon: bool = False,
) -> ModelMesh:
    m = deepcopy(mesh)
    if m.links_ids.size == 0 or m.links_weights.size == 0:
        return m

    source_bones = source_scene.skeleton.bones
    target_bones_by_name = _build_bone_name_index(target_scene)

    src_id_to_target: dict[int, int] = {}
    for src_idx, _ in enumerate(source_bones):
        target_idx = _resolve_target_from_source_chain(source_bones, src_idx, target_bones_by_name)
        if target_idx is not None:
            src_id_to_target[int(src_idx)] = int(target_idx)

    if not is_weapon and m.positions.size > 0:
        src_global_mats = _calc_global_mats(source_scene)
        tgt_global_mats = _calc_global_mats(target_scene)

        pos = m.positions.astype(np.float32)
        nrm = m.normals.astype(np.float32) if m.normals.size > 0 else None
        pos_h = np.concatenate([pos, np.ones((pos.shape[0], 1), dtype=np.float32)], axis=1)

        out_pos = np.zeros_like(pos)
        out_nrm = np.zeros_like(nrm) if nrm is not None else None

        for slot in range(m.links_ids.shape[1]):
            w = m.links_weights[:, slot]
            ids = m.links_ids[:, slot]

            for src_idx, tgt_idx in src_id_to_target.items():
                mask = (w > 0) & (ids == src_idx)
                if not np.any(mask):
                    continue

                corr = tgt_global_mats[tgt_idx] @ np.linalg.inv(src_global_mats[src_idx])

                out_pos[mask] += (pos_h[mask] @ corr.T)[:, :3] * w[mask][:, None]

                if nrm is not None and out_nrm is not None:
                    out_nrm[mask] += (nrm[mask] @ corr[:3, :3].T) * w[mask][:, None]

        m.positions = out_pos.astype(np.float32)
        if out_nrm is not None:
            norms = np.linalg.norm(out_nrm, axis=1, keepdims=True)
            m.normals = (out_nrm / np.where(norms > 1e-8, norms, 1.0)).astype(np.float32)

    ids = m.links_ids.astype(np.int32).copy()
    weights = m.links_weights.astype(np.float32).copy()
    out_ids = np.zeros_like(ids, dtype=np.uint8)
    matched = np.zeros_like(ids, dtype=bool)

    for src_id, target_idx in src_id_to_target.items():
        mask = ids == src_id
        out_ids[mask] = np.uint8(target_idx)
        matched[mask] = True

    weights[~matched] = 0.0

    sums = weights.sum(axis=1, keepdims=True)
    zero_mask = sums[:, 0] <= 1e-8
    if np.any(zero_mask):
        fallback_idx = target_bones_by_name.get("wpn_body", 0)
        out_ids[zero_mask, 0] = np.uint8(fallback_idx)
        weights[zero_mask, 0] = 1.0
        sums[zero_mask, 0] = 1.0

    m.links_ids = out_ids.astype(np.uint8)
    m.links_weights = (weights / sums).astype(np.float32)
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
                is_weapon=True,
            )
        )

    output.scene.count.meshes = len(output.scene.meshes)

    with formats.glb.GlbEncoder(output, options) as glb:
        glb.encode()
        glb.export("F:/tmp/retarget/test")
