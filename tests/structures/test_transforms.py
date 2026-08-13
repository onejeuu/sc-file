import numpy as np
import pytest

from scfile.exceptions import AnimationError
from scfile.structures import models as S
from scfile.structures.content import ModelContent
from scfile.structures.models import transforms as T


def test_unique_names() -> None:
    scene = S.ModelScene(meshes=[S.ModelMesh(name="mesh"), S.ModelMesh(name="mesh")])

    result = T.unique_names(scene)

    assert [mesh.name for mesh in result.meshes] == ["mesh", "mesh_2"]
    assert [mesh.name for mesh in scene.meshes] == ["mesh", "mesh"]


def test_flip_uv() -> None:
    mesh = S.ModelMesh(uv1=np.array([[0.0, 0.0]], dtype=np.float32))
    scene = S.ModelScene(meshes=[mesh])

    result = T.flip_uv(scene)

    assert result.meshes[0].uv1[0, 1] == 1.0
    assert mesh.uv1[0, 1] == 0.0


def test_uv_transforms_preserve_normalized_meshes() -> None:
    flipped = S.ModelMesh(uv_origin=S.UVOrigin.BOTTOM_LEFT, uv_sign=S.UVSign.POSITIVE)
    inverted = S.ModelMesh(uv_sign=S.UVSign.NEGATIVE)

    assert T.flip_uv(S.ModelScene(meshes=[flipped])).meshes[0] is flipped
    assert T.invert_uv(S.ModelScene(meshes=[inverted])).meshes[0] is inverted


def test_skeleton_to_local() -> None:
    skeleton = S.ModelSkeleton(
        bones=[
            S.SkeletonBone(id=0, position=np.array([0.0, 1.0, 0.0], dtype=np.float32)),
            S.SkeletonBone(id=1, parent_id=0, position=np.array([0.0, 3.0, 0.0], dtype=np.float32)),
        ],
        space=S.SkeletonSpace.GLOBAL,
    )

    result = T.skeleton_to_local(S.ModelScene(skeleton=skeleton))

    assert np.array_equal(result.skeleton.bones[1].position, [0.0, 2.0, 0.0])
    assert skeleton.space is S.SkeletonSpace.GLOBAL


def test_invert_uv() -> None:
    mesh = S.ModelMesh(uv1=np.array([[0.0, 0.25]], dtype=np.float32))

    result = T.invert_uv(S.ModelScene(meshes=[mesh]))

    assert result.meshes[0].uv1[0, 1] == -0.25
    assert result.meshes[0].uv_sign is S.UVSign.NEGATIVE
    assert mesh.uv1[0, 1] == 0.25


def test_scene_transforms() -> None:
    mesh = S.ModelMesh(uv1=np.array([[0.0, 0.25]], dtype=np.float32))
    data = ModelContent(scene=S.ModelScene(meshes=[mesh]))
    (transform,) = T.scene_transforms(T.flip_uv)

    result = transform(data)

    assert result is not data
    assert result.scene.meshes[0].uv1[0, 1] == 0.75
    assert data.scene.meshes[0].uv1[0, 1] == 0.25


def test_global_transforms() -> None:
    skeleton = S.ModelSkeleton(
        bones=[
            S.SkeletonBone(id=0, position=np.array([1.0, 0.0, 0.0], dtype=np.float32)),
            S.SkeletonBone(id=1, parent_id=0, position=np.array([0.0, 2.0, 0.0], dtype=np.float32)),
        ]
    )

    transforms = T.global_transforms(skeleton)

    assert np.allclose(transforms[1][:3, 3], [1.0, 2.0, 0.0])
    assert np.allclose(T.inverse_bind_matrices(skeleton)[1] @ transforms[1], np.eye(4))


def test_inverse_bind_matrices_empty_and_transposed() -> None:
    assert T.inverse_bind_matrices(S.ModelSkeleton()).shape == (0, 4, 4)

    skeleton = S.ModelSkeleton(bones=[S.SkeletonBone(position=np.array([1.0, 2.0, 3.0]))])
    regular = T.inverse_bind_matrices(skeleton)
    transposed = T.inverse_bind_matrices(skeleton, transpose=True)
    assert np.array_equal(transposed, regular.transpose(0, 2, 1))


def test_skeleton_to_local_is_idempotent() -> None:
    scene = S.ModelScene(skeleton=S.ModelSkeleton(space=S.SkeletonSpace.LOCAL))

    assert T.skeleton_to_local(scene) is scene


def test_animation_to_absolute() -> None:
    clip = S.AnimationClip(
        frames=1,
        translations=np.zeros((1, 1, 3), dtype=np.float32),
    )
    skeleton = S.ModelSkeleton(bones=[S.SkeletonBone(position=np.array([1.0, 2.0, 3.0], dtype=np.float32))])
    scene = S.ModelScene(skeleton=skeleton, animation=S.ModelAnimation(clips=[clip]))

    result = T.animation_to_absolute(scene)

    assert np.array_equal(result.animation.clips[0].translations[0, 0], [1.0, 2.0, 3.0])
    assert result.animation.translation is S.AnimationTranslation.ABSOLUTE
    assert np.array_equal(scene.animation.clips[0].translations[0, 0], [0.0, 0.0, 0.0])


def test_animation_to_absolute_preserves_absolute_and_empty_clips() -> None:
    absolute = S.ModelScene(animation=S.ModelAnimation(translation=S.AnimationTranslation.ABSOLUTE))
    assert T.animation_to_absolute(absolute) is absolute

    clip = S.AnimationClip()
    scene = S.ModelScene(animation=S.ModelAnimation(clips=[clip]))
    result = T.animation_to_absolute(scene)
    assert result.animation.clips[0] is clip


def test_apply_fp_animation() -> None:
    animation = S.ModelScene(
        meshes=[S.ModelMesh(name="animation")],
        skeleton=S.ModelSkeleton(bones=[S.SkeletonBone(id=0, name="root")]),
        animation=S.ModelAnimation(clips=[S.AnimationClip()]),
    )
    mesh = S.ModelMesh(
        name="model",
        links_ids=np.array([[0, 0, 0, 0]], dtype=np.uint8),
        links_weights=np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32),
        link_space=S.LinkSpace.LOCAL,
    )
    model = S.ModelScene(meshes=[mesh], skeleton=S.ModelSkeleton(bones=[S.SkeletonBone(id=0, name="root")]))

    result = T.apply_fp_animation(animation, model)

    assert [mesh.name for mesh in result.meshes] == ["animation", "model"]
    assert result.meshes[1].link_space is S.LinkSpace.GLOBAL
    assert model.meshes[0].link_space is S.LinkSpace.LOCAL


def _fp_scene(*, clips: bool = True, duplicate_bones: bool = False) -> S.ModelScene:
    bones = [S.SkeletonBone(id=0, name="root")]
    if duplicate_bones:
        bones.append(S.SkeletonBone(id=1, name="root"))
    animation = S.ModelAnimation(clips=[S.AnimationClip()] if clips else [])
    return S.ModelScene(skeleton=S.ModelSkeleton(bones=bones), animation=animation)


def _skinned_model(bone_id: int = 0, bone_name: str = "root") -> S.ModelScene:
    mesh = S.ModelMesh(
        links_ids=np.array([[bone_id, 0, 0, 0]], dtype=np.uint8),
        links_weights=np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32),
    )
    return S.ModelScene(meshes=[mesh], skeleton=S.ModelSkeleton(bones=[S.SkeletonBone(id=0, name=bone_name)]))


def test_apply_fp_animation_validates_inputs() -> None:
    with pytest.raises(AnimationError):
        T.apply_fp_animation(_fp_scene(clips=False), _skinned_model())

    with pytest.raises(AnimationError):
        T.apply_fp_animation(_fp_scene())

    with pytest.raises(AnimationError):
        T.apply_fp_animation(_fp_scene(duplicate_bones=True), _skinned_model())

    with pytest.raises(AnimationError):
        T.apply_fp_animation(_fp_scene(), _skinned_model(bone_id=1))

    with pytest.raises(AnimationError):
        T.apply_fp_animation(_fp_scene(), _skinned_model(bone_name="missing"))


def test_apply_skins() -> None:
    def mesh(name: str) -> S.ModelMesh:
        return S.ModelMesh(
            name=name,
            links_ids=np.zeros((1, 4), dtype=np.uint8),
            links_weights=np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32),
        )

    animation = S.ModelScene(
        meshes=[mesh("animation")],
        skeleton=S.ModelSkeleton(bones=[S.SkeletonBone(id=0, name="root")]),
    )
    model = S.ModelScene(
        meshes=[mesh("model")],
        skeleton=S.ModelSkeleton(bones=[S.SkeletonBone(id=0, name="root")]),
    )
    scene = S.ModelScene(meshes=[*animation.meshes, *model.meshes], skeleton=animation.skeleton)

    result = T.apply_skins(scene, animation, model)

    assert [mesh.skin for mesh in result.meshes] == [0, 1]
    assert len(result.skins) == 2
    assert not scene.skins


def test_apply_skins_handles_unskinned_and_partial_skeletons() -> None:
    animation = S.ModelScene(skeleton=S.ModelSkeleton(bones=[S.SkeletonBone(id=0, name="root")]))
    unskinned = S.ModelScene(meshes=[S.ModelMesh()])
    partial = _skinned_model(bone_name="other")
    scene = S.ModelScene(meshes=[*unskinned.meshes, *partial.meshes], skeleton=animation.skeleton)

    result = T.apply_skins(scene, animation, unskinned, partial)

    assert result.meshes[0].skin is None
    assert result.meshes[1].skin == 0
    assert len(result.skins) == 1


def test_animation_library() -> None:
    clip = S.AnimationClip(
        frames=1,
        translations=np.zeros((1, 1, 3), dtype=np.float32),
        rotations=np.zeros((1, 1, 4), dtype=np.float32),
    )
    library = S.ModelScene(animation=S.ModelAnimation(clips=[clip]))
    model = S.ModelScene(skeleton=S.ModelSkeleton(bones=[S.SkeletonBone()]))

    result = T.apply_animation_library(library, model)

    assert result.animation.clips == [clip]
    assert not model.animation.clips


def test_animation_library_validates_clips_and_bones() -> None:
    model = S.ModelScene(skeleton=S.ModelSkeleton(bones=[S.SkeletonBone()]))
    with pytest.raises(AnimationError):
        T.apply_animation_library(S.ModelScene(), model)

    clip = S.AnimationClip(translations=np.zeros((1, 2, 3), dtype=np.float32))
    library = S.ModelScene(animation=S.ModelAnimation(clips=[clip]))
    with pytest.raises(AnimationError):
        T.apply_animation_library(library, model)


def test_morph_animation() -> None:
    clip = S.AnimationClip(frames=1, morph_weights=np.zeros((1, 1), dtype=np.float32))
    animation = S.ModelScene(animation=S.ModelAnimation(clips=[clip], morph_channels=["smile"]))
    model = S.ModelScene(meshes=[S.ModelMesh(blend_shapes=[S.BlendShape(channel="smile")])])

    result = T.apply_morph_animation(animation, model)

    assert result.animation.clips == [clip]
    assert not model.animation.clips


def test_morph_animation_validates_compatibility() -> None:
    empty_model = S.ModelScene()
    with pytest.raises(AnimationError):
        T.apply_morph_animation(S.ModelScene(), empty_model)

    clip = S.AnimationClip(morph_weights=np.ones((1, 1), dtype=np.float32))
    duplicate = S.ModelScene(animation=S.ModelAnimation(clips=[clip], morph_channels=["smile", "smile"]))
    with pytest.raises(AnimationError):
        T.apply_morph_animation(duplicate, empty_model)

    animation = S.ModelScene(animation=S.ModelAnimation(clips=[clip], morph_channels=["smile"]))
    with pytest.raises(AnimationError):
        T.apply_morph_animation(animation, empty_model)

    model = S.ModelScene(meshes=[S.ModelMesh(blend_shapes=[S.BlendShape(channel="blink")])])
    with pytest.raises(AnimationError):
        T.apply_morph_animation(animation, model)
