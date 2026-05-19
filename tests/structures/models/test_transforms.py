import numpy as np
import pytest

from scfile.structures import models as S
from scfile.structures.models import transforms as T


def test_unique_names_empty():
    scene = S.ModelScene()
    result = T.unique_names(scene)
    assert result.meshes == []


def test_unique_names_single():
    mesh = S.ModelMesh(name="mesh")
    scene = S.ModelScene(meshes=[mesh])
    result = T.unique_names(scene)
    assert result.meshes[0].name == "mesh"


def test_unique_names_duplicates():
    scene = S.ModelScene(meshes=[S.ModelMesh(name="mesh") for _ in range(3)])
    result = T.unique_names(scene)
    assert [m.name for m in result.meshes] == ["mesh", "mesh_2", "mesh_3"]


def test_unique_names_empty_name():
    scene = S.ModelScene(meshes=[S.ModelMesh(name="")])
    result = T.unique_names(scene)
    assert result.meshes[0].name == "noname"


def test_unique_names_mixed():
    scene = S.ModelScene(
        meshes=[
            S.ModelMesh(name="a"),
            S.ModelMesh(name="b"),
            S.ModelMesh(name="a"),
        ]
    )
    result = T.unique_names(scene)
    assert [m.name for m in result.meshes] == ["a", "b", "a_2"]


def test_unique_names_does_not_mutate():
    mesh = S.ModelMesh(name="original")
    scene = S.ModelScene(meshes=[mesh])
    T.unique_names(scene)
    assert scene.meshes[0].name == "original"


def test_flip_uv():
    mesh = S.ModelMesh(
        uv1=np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32),
        uv2=np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32),
        uv_origin=S.UVOrigin.TOP_LEFT,
        uv_sign=S.UVSign.POSITIVE,
    )
    scene = S.ModelScene(meshes=[mesh])
    result = T.flip_uv(scene)
    m = result.meshes[0]
    assert m.uv_origin == S.UVOrigin.BOTTOM_LEFT
    assert m.uv_sign == S.UVSign.POSITIVE
    assert np.allclose(m.uv1[:, 1], [1.0, 0.0])
    assert np.allclose(m.uv2[:, 1], [1.0, 0.0])


def test_invert_uv():
    mesh = S.ModelMesh(
        uv1=np.array([[0.0, 0.5]], dtype=np.float32),
        uv2=np.array([[0.0, 0.5]], dtype=np.float32),
        uv_sign=S.UVSign.POSITIVE,
    )
    scene = S.ModelScene(meshes=[mesh])
    result = T.invert_uv(scene)
    m = result.meshes[0]
    assert m.uv_sign == S.UVSign.NEGATIVE
    assert np.allclose(m.uv1[:, 1], [-0.5])
    assert np.allclose(m.uv2[:, 1], [-0.5])


@pytest.mark.parametrize(
    "transform, build_scene",
    [
        (
            T.flip_uv,
            lambda: S.ModelScene(
                meshes=[
                    S.ModelMesh(
                        uv_origin=S.UVOrigin.BOTTOM_LEFT,
                        uv_sign=S.UVSign.POSITIVE,
                    )
                ]
            ),
        ),
        (
            T.invert_uv,
            lambda: S.ModelScene(meshes=[S.ModelMesh(uv_sign=S.UVSign.NEGATIVE)]),
        ),
        (
            T.skeleton_to_local,
            lambda: S.ModelScene(skeleton=S.ModelSkeleton(space=S.SkeletonSpace.LOCAL)),
        ),
        (
            T.build_hierarchy,
            lambda: S.ModelScene(skeleton=S.ModelSkeleton(hierarchy=S.SkeletonHierarchy.BUILT)),
        ),
    ],
)
def test_skip_if_done(transform, build_scene):
    scene = build_scene()
    result = transform(scene)
    assert result.meshes == scene.meshes
    assert result.skeleton == scene.skeleton


def test_skeleton_root_stays():
    root = S.SkeletonBone(id=0, parent_id=-1, position=np.array([1.0, 2.0, 3.0]))
    skeleton = S.ModelSkeleton(bones=[root], space=S.SkeletonSpace.GLOBAL)
    scene = S.ModelScene(skeleton=skeleton)
    result = T.skeleton_to_local(scene)
    assert np.allclose(result.skeleton.bones[0].position, [1.0, 2.0, 3.0])


def test_skeleton_to_local_child():
    root = S.SkeletonBone(id=0, parent_id=-1, position=np.array([0.0, 0.0, 0.0]))
    child = S.SkeletonBone(id=1, parent_id=0, position=np.array([0.0, 1.0, 0.0]))
    skeleton = S.ModelSkeleton(bones=[root, child], space=S.SkeletonSpace.GLOBAL)
    scene = S.ModelScene(skeleton=skeleton)
    result = T.skeleton_to_local(scene)
    assert np.allclose(result.skeleton.bones[1].position, [0.0, 1.0, 0.0])


def test_skeleton_to_local_grandchild():
    root = S.SkeletonBone(id=0, parent_id=-1, position=np.array([0.0, 0.0, 0.0]))
    child = S.SkeletonBone(id=1, parent_id=0, position=np.array([0.0, 1.0, 0.0]))
    grandchild = S.SkeletonBone(id=2, parent_id=1, position=np.array([0.0, 2.0, 0.0]))
    skeleton = S.ModelSkeleton(bones=[root, child, grandchild], space=S.SkeletonSpace.GLOBAL)
    scene = S.ModelScene(skeleton=skeleton)
    result = T.skeleton_to_local(scene)
    assert np.allclose(result.skeleton.bones[2].position, [0.0, 1.0, 0.0])


def test_skeleton_to_local_sets_space():
    skeleton = S.ModelSkeleton(space=S.SkeletonSpace.GLOBAL)
    scene = S.ModelScene(skeleton=skeleton)
    result = T.skeleton_to_local(scene)
    assert result.skeleton.space == S.SkeletonSpace.LOCAL


def test_skeleton_build_hierarchy():
    root = S.SkeletonBone(id=0, parent_id=-1)
    child = S.SkeletonBone(id=1, parent_id=0)
    skeleton = S.ModelSkeleton(bones=[root, child], hierarchy=S.SkeletonHierarchy.FLAT)
    scene = S.ModelScene(skeleton=skeleton)
    result = T.build_hierarchy(scene)
    assert result.skeleton.hierarchy == S.SkeletonHierarchy.BUILT
    assert result.skeleton.bones[0].children == [result.skeleton.bones[1]]


def test_skeleton_no_children():
    root = S.SkeletonBone(id=0, parent_id=-1)
    skeleton = S.ModelSkeleton(bones=[root], hierarchy=S.SkeletonHierarchy.FLAT)
    scene = S.ModelScene(skeleton=skeleton)
    result = T.build_hierarchy(scene)
    assert result.skeleton.bones[0].children == []


def test_animation_to_absolute():
    root = S.SkeletonBone(id=0, parent_id=-1, position=np.array([0.0, 0.0, 0.0]))
    child = S.SkeletonBone(id=1, parent_id=0, position=np.array([0.0, 1.0, 0.0]))
    skeleton = S.ModelSkeleton(bones=[root, child], space=S.SkeletonSpace.LOCAL)

    clip = S.AnimationClip(
        frames=2,
        translations=np.zeros((2, 2, 3), dtype=np.float32),
        rotations=np.zeros((2, 2, 4), dtype=np.float32),
    )
    clip.translations[:, 0, :] = [1.0, 0.0, 0.0]
    clip.translations[:, 1, :] = [0.0, 2.0, 0.0]

    animation = S.ModelAnimation(clips=[clip], translation=S.AnimationTranslation.DELTA)
    scene = S.ModelScene(skeleton=skeleton, animation=animation)
    result = T.animation_to_absolute(scene)

    assert result.animation.translation == S.AnimationTranslation.ABSOLUTE
    assert np.allclose(result.animation.clips[0].translations[0, 0], [1.0, 0.0, 0.0])
    assert np.allclose(result.animation.clips[0].translations[0, 1], [0.0, 3.0, 0.0])
    assert np.allclose(result.animation.clips[0].rotations, clip.rotations)


def test_animation_to_absolute_skip():
    animation = S.ModelAnimation(translation=S.AnimationTranslation.ABSOLUTE)
    scene = S.ModelScene(animation=animation)
    result = T.animation_to_absolute(scene)
    assert result is scene
