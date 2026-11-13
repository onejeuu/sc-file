import pytest

from scfile.content import ModelContent
from scfile.content.models import Feature
from scfile.enums import FileFormat
from scfile.options import BlockMapping, DEFAULT_OUTPUT_FORMATS, Options


def test_block_mapping_alias_is_raw_string_dict() -> None:
    assert BlockMapping.__value__ == dict[str, str]


def test_animation() -> None:
    assert not Options().mcal_extended
    assert Options(animation=True).skeleton_enabled
    assert Options(animation=True).model_features == (Feature.SKELETON, Feature.ANIMATION)


def test_targets() -> None:
    assert Options().output_formats == DEFAULT_OUTPUT_FORMATS
    assert Options(skeleton=True).output_formats[ModelContent] is FileFormat.GLB
    assert Options(output_formats={ModelContent: FileFormat.FBX}).output_formats[ModelContent] is FileFormat.FBX


@pytest.mark.parametrize(
    ("value", "expected"),
    ((-1, 0), (0, 0), (1, 1), (3, 3)),
)
def test_ol_max_mipmaps(value: int, expected: int) -> None:
    assert Options().ol_max_mipmaps is None
    assert Options(ol_max_mipmaps=value).ol_max_mipmaps == expected


