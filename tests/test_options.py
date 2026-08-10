from dataclasses import fields
from typing import get_type_hints

from scfile.options import (
    DEFAULT_MODEL_FORMAT,
    DEFAULT_SKELETON_FORMAT,
    ModelConfig,
    ModelOptions,
    Options,
    RegionConfig,
    RegionOptions,
)
from scfile.structures.models import Feature


def test_animation_enables_skeleton() -> None:
    assert Options(model={"animation": True}).model.skeleton_enabled
    assert Options(model={"animation": True}).model.features == (Feature.SKELETON, Feature.ANIMATION)


def test_default_format() -> None:
    assert Options().default_format is DEFAULT_MODEL_FORMAT
    assert Options(model={"skeleton": True}).default_format is DEFAULT_SKELETON_FORMAT
    assert Options(model={"animation": True}).default_format is DEFAULT_SKELETON_FORMAT


def test_model_config() -> None:
    assert get_type_hints(ModelConfig) == {field.name: field.type for field in fields(ModelOptions)}


def test_region_config() -> None:
    assert get_type_hints(RegionConfig) == {field.name: field.type for field in fields(RegionOptions)}


def test_copy_is_independent() -> None:
    options = Options(model={"skeleton": True}, region={"raw_blocks": True})
    copied = options.copy()
    copied.model.animation = True
    copied.region.full_chunk = True

    assert options.model.animation is False
    assert options.region.full_chunk is False
    assert copied.model.animation is True
    assert copied.region.full_chunk is True
