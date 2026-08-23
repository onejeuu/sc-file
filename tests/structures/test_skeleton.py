import numpy as np

from scfile.content.models import ROOT_BONE_ID, ModelSkeleton, SkeletonBone


def test_roots() -> None:
    root = SkeletonBone(id=0, parent_id=ROOT_BONE_ID)
    child = SkeletonBone(id=1, parent_id=0)

    assert ModelSkeleton([root, child]).roots == [root]


def test_quaternion() -> None:
    bone = SkeletonBone(rotation=np.zeros(3, dtype=np.float32))

    assert np.allclose(bone.quaternion, [0.0, 0.0, 0.0, 1.0])


def test_slug() -> None:
    assert SkeletonBone(name="Bone #1 (Top)").slug == "bone1top"
