import numpy as np
import pytest

from scfile.exceptions import AnimationError
from scfile.structures import models as S
from tools.cmd.audit.relations import arms


def test_clip_motion_ignores_quaternion_sign() -> None:
    static = S.AnimationClip(
        frames=2,
        rotations=np.array([[[0.0, 0.0, 0.0, 1.0]], [[0.0, 0.0, 0.0, -1.0]]], dtype=np.float32),
    )
    moving = S.AnimationClip(
        frames=2,
        rotations=np.array([[[0.0, 0.0, 0.0, 1.0]], [[0.0, 0.0, 1.0, 0.0]]], dtype=np.float32),
    )

    assert not arms._clip_moves(static)
    assert arms._clip_moves(moving)


def test_validate_result_rejects_lost_mesh() -> None:
    clip = S.AnimationClip(
        frames=2,
        translations=np.array([[[0.0, 0.0, 0.0]], [[1.0, 0.0, 0.0]]], dtype=np.float32),
        rotations=np.array([[[0.0, 0.0, 0.0, 1.0]]] * 2, dtype=np.float32),
    )
    source = S.ModelScene(
        skeleton=S.ModelSkeleton(bones=[S.SkeletonBone(name="root")]),
        animation=S.ModelAnimation(clips=[clip]),
    )
    model = S.ModelScene(meshes=[S.ModelMesh()])

    with pytest.raises(AnimationError, match="lost 1 meshes"):
        arms._validate_result(source, [model], source)
