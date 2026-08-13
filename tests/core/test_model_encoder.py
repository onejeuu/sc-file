import numpy as np

from scfile.core import ModelEncoder
from scfile.enums import FileFormat
from scfile.options import Options
from scfile.structures.content import ModelContent
from scfile.structures.models import AnimationClip, Feature, ModelMesh, SkeletonBone


class ModelEncoderStub(ModelEncoder):
    format = FileFormat.OBJ
    features = (Feature.UV, Feature.SKELETON, Feature.BONE_ANIMATION)

    def _serialize(self) -> None:
        pass


def test_supports() -> None:
    assert ModelEncoderStub.supports(Feature.UV)
    assert ModelEncoderStub.supports(Feature.ANIMATION)
    assert not ModelEncoderStub.supports(Feature.NORMALS)


def test_includes() -> None:
    data = ModelContent()
    data.scene.meshes.append(ModelMesh(uv1=np.zeros((1, 2), dtype=np.float32)))
    data.scene.skeleton.bones.append(SkeletonBone())
    data.scene.animation.clips.append(
        AnimationClip(
            translations=np.zeros((1, 3), dtype=np.float32),
            rotations=np.zeros((1, 4), dtype=np.float32),
        )
    )

    with ModelEncoderStub(data, Options(model={"animation": True})) as encoder:
        assert encoder.includes(Feature.UV)
        assert encoder.includes(Feature.SKELETON)
        assert encoder.includes(Feature.BONE_ANIMATION)
        assert encoder.includes(Feature.ANIMATION)
        assert not encoder.includes(Feature.NORMALS)


def test_disabled_features() -> None:
    data = ModelContent()
    data.scene.skeleton.bones.append(SkeletonBone())
    data.scene.animation.clips.append(
        AnimationClip(
            translations=np.zeros((1, 3), dtype=np.float32),
            rotations=np.zeros((1, 4), dtype=np.float32),
        )
    )

    with ModelEncoderStub(data) as encoder:
        assert not encoder.includes(Feature.SKELETON)
        assert not encoder.includes(Feature.ANIMATION)
