import pytest

from scfile.content import ModelContent
from scfile.content.models import Feature
from scfile.enums import FileFormat
from scfile.options import DEFAULT_TARGETS, Options


def test_animation() -> None:
    assert not Options().preserve_clips
    assert Options(animation=True).skeleton_enabled
    assert Options(animation=True).model_features == (Feature.SKELETON, Feature.ANIMATION)


def test_targets() -> None:
    assert Options().targets == DEFAULT_TARGETS
    assert Options(skeleton=True).targets[ModelContent] is FileFormat.GLB
    assert Options(targets={ModelContent: FileFormat.FBX}).targets[ModelContent] is FileFormat.FBX


@pytest.mark.parametrize(
    ("value", "expected"),
    ((-1, 0), (0, 0), (1, 1), (3, 3)),
)
def test_max_mipmaps(value: int, expected: int) -> None:
    assert Options().max_mipmaps is None
    assert Options(max_mipmaps=value).max_mipmaps == expected
