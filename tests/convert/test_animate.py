import json
import struct
from collections import defaultdict

import numpy as np

from scfile.core import ModelContent, Options
from scfile.formats import GlbEncoder
from scfile.structures import models as S
from scfile.structures.models import transforms as T


def _content(*names: str, mesh_bone: int | None = None) -> ModelContent:
    content = ModelContent(flags=defaultdict(bool, {S.Flag.SKELETON: True}))
    content.scene.skeleton.bones = [
        S.SkeletonBone(id=index, name=name, parent_id=index - 1)
        for index, name in enumerate(names)
    ]

    if content.scene.skeleton.bones:
        content.scene.skeleton.bones[0].parent_id = -1

    if mesh_bone is not None:
        content.scene.meshes.append(
            S.ModelMesh(
                vertices=np.zeros((1, 3), dtype=np.float32),
                links_ids=np.array([[mesh_bone, 0, 0, 0]], dtype=np.uint8),
                links_weights=np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32),
            )
        )

    return content


def _clip(bones: int) -> S.AnimationClip:
    rotations = np.zeros((1, bones, 4), dtype=np.float32)
    rotations[:, :, 3] = 1.0
    return S.AnimationClip(
        frames=1,
        translations=np.zeros((1, bones, 3), dtype=np.float32),
        rotations=rotations,
    )


def test_apply_animation_multiple_models():
    animation = _content("root", "weapon", "hand")
    animation.scene.animation.clips.append(_clip(3))
    hands = _content("root", "hand", mesh_bone=1)
    weapon = _content("root", "weapon", mesh_bone=1)

    scene = T.apply_animation(animation.scene, hands.scene, weapon.scene)

    assert len(scene.meshes) == 2
    assert scene.meshes[0].links_ids[0, 0] == 2
    assert scene.meshes[1].links_ids[0, 0] == 1

    result = ModelContent(flags=animation.flags, scene=scene)
    bindpose = scene.skeleton.inverse_bind_matrices(transpose=False)

    with GlbEncoder(result, Options(skeleton=True)) as glb:
        glb.ctx["SKINS"] = [bindpose, bindpose]
        glb.ctx["MESH_SKINS"] = [0, 1]
        data = glb.getvalue()

    length = struct.unpack_from("<I", data, 12)[0]
    document = json.loads(data[20 : 20 + length])
    assert len(document["skins"]) == 2
    assert [node["skin"] for node in document["nodes"][:2]] == [0, 1]
