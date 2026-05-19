import numpy as np

from scfile.consts import ModelDefaults
from scfile.structures import models as S


ROOT = ModelDefaults.ROOT_BONE_ID


def test_roots_single():
    root = S.SkeletonBone(id=0, parent_id=ROOT)
    skeleton = S.ModelSkeleton(bones=[root])
    assert skeleton.roots == [root]


def test_roots_multiple():
    root1 = S.SkeletonBone(id=0, parent_id=ROOT)
    root2 = S.SkeletonBone(id=1, parent_id=ROOT)
    child = S.SkeletonBone(id=2, parent_id=0)
    skeleton = S.ModelSkeleton(bones=[root1, root2, child])
    assert skeleton.roots == [root1, root2]


def test_global_single():
    bone = S.SkeletonBone(
        id=0,
        parent_id=ROOT,
        position=np.array([1.0, 2.0, 3.0], dtype=np.float32),
    )
    skeleton = S.ModelSkeleton(bones=[bone])
    result = skeleton.calculate_global_transforms()
    assert len(result) == 1
    assert np.allclose(result[0][:3, 3], [1.0, 2.0, 3.0])


def test_global_chain():
    root = S.SkeletonBone(
        id=0,
        parent_id=ROOT,
        position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
    )
    child = S.SkeletonBone(
        id=1,
        parent_id=0,
        position=np.array([0.0, 1.0, 0.0], dtype=np.float32),
    )
    skeleton = S.ModelSkeleton(bones=[root, child])
    result = skeleton.calculate_global_transforms()
    assert np.allclose(result[1][:3, 3], [0.0, 1.0, 0.0])


def test_global_deep():
    root = S.SkeletonBone(
        id=0,
        parent_id=ROOT,
        position=np.array([1.0, 0.0, 0.0], dtype=np.float32),
    )
    child = S.SkeletonBone(
        id=1,
        parent_id=0,
        position=np.array([0.0, 1.0, 0.0], dtype=np.float32),
    )
    grandchild = S.SkeletonBone(
        id=2,
        parent_id=1,
        position=np.array([0.0, 0.0, 1.0], dtype=np.float32),
    )
    skeleton = S.ModelSkeleton(bones=[root, child, grandchild])
    result = skeleton.calculate_global_transforms()
    assert np.allclose(result[2][:3, 3], [1.0, 1.0, 1.0])


def test_ibm_shape():
    root = S.SkeletonBone(id=0, parent_id=ROOT)
    skeleton = S.ModelSkeleton(bones=[root])
    result = skeleton.inverse_bind_matrices(transpose=False)
    assert result.shape == (1, 4, 4)


def test_ibm_transpose():
    root = S.SkeletonBone(id=0, parent_id=ROOT)
    child = S.SkeletonBone(id=1, parent_id=0)
    skeleton = S.ModelSkeleton(bones=[root, child])
    result = skeleton.inverse_bind_matrices(transpose=True)
    assert result.shape == (2, 4, 4)


def test_ibm_invert():
    root = S.SkeletonBone(
        id=0,
        parent_id=ROOT,
        position=np.array([1.0, 0.0, 0.0], dtype=np.float32),
    )
    skeleton = S.ModelSkeleton(bones=[root])
    ibm = skeleton.inverse_bind_matrices(transpose=False)
    gt = skeleton.calculate_global_transforms()[0]
    assert np.allclose(ibm[0] @ gt, np.eye(4), atol=1e-6)


def test_quat():
    bone = S.SkeletonBone(rotation=np.array([0.0, 0.0, 0.0], dtype=np.float32))
    assert np.allclose(bone.quaternion, [0.0, 0.0, 0.0, 1.0])


def test_slug():
    bone = S.SkeletonBone(name="Left Arm")
    assert bone.slug == "leftarm"


def test_slug_specials():
    bone = S.SkeletonBone(name="Bone #1 (Top)")
    assert bone.slug == "bone1top"
