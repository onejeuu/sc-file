from scfile.enums import FileFormat
from scfile.options import DEFAULT_TARGETS, Options
from scfile.structures.content import ModelContent
from scfile.structures.models import Feature


def test_animation() -> None:
    assert not Options().raw_clips
    assert Options(animation=True).skeleton_enabled
    assert Options(animation=True).model_features == (Feature.SKELETON, Feature.ANIMATION)


def test_targets() -> None:
    assert Options().targets == DEFAULT_TARGETS
    assert Options(skeleton=True).targets[ModelContent] is FileFormat.GLB
    assert Options(targets={ModelContent: FileFormat.FBX}).targets[ModelContent] is FileFormat.FBX
