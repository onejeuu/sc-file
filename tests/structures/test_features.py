import numpy as np

from scfile.content.models import AnimationClip, BlendShape, Feature, ModelMesh, ModelScene, SkeletonBone


def test_mesh() -> None:
    scene = ModelScene(meshes=[ModelMesh(uv1=np.zeros((1, 2), dtype=np.float32))])

    assert scene.has(Feature.UV)
    assert not scene.has(Feature.NORMALS)


def test_attributes() -> None:
    mesh = ModelMesh(
        uv2=np.zeros((1, 2), dtype=np.float32),
        normals=np.zeros((1, 3), dtype=np.float32),
        tangents=np.zeros((1, 4), dtype=np.float32),
        colors=np.zeros((1, 4), dtype=np.uint8),
    )
    scene = ModelScene(meshes=[mesh])

    assert scene.has(Feature.UV2)
    assert scene.has(Feature.NORMALS)
    assert scene.has(Feature.TANGENTS)
    assert scene.has(Feature.COLORS)


def test_skeleton() -> None:
    scene = ModelScene()
    scene.skeleton.bones.append(SkeletonBone())

    assert scene.has(Feature.SKELETON)


def test_animation() -> None:
    scene = ModelScene()
    scene.animation.clips.append(
        AnimationClip(
            translations=np.zeros((1, 3), dtype=np.float32),
            rotations=np.zeros((1, 4), dtype=np.float32),
        )
    )

    assert scene.has(Feature.BONE_ANIMATION)
    assert scene.has(Feature.ANIMATION)


def test_morph_animation() -> None:
    scene = ModelScene()
    scene.animation.clips.append(AnimationClip(morph_weights=np.zeros((1, 1), dtype=np.float32)))

    assert scene.has(Feature.MORPH_ANIMATION)
    assert scene.has(Feature.ANIMATION)


def test_blend_shapes() -> None:
    scene = ModelScene(meshes=[ModelMesh(blend_shapes=[BlendShape()])])

    assert scene.has(Feature.BLEND_SHAPES)
