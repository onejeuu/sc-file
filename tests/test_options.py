from dataclasses import fields
from typing import get_type_hints

from scfile.options import (
    DEFAULT_TARGETS,
    ModelConfig,
    ModelOptions,
    Options,
    RegionConfig,
    RegionOptions,
)
from scfile.enums import FileFormat
from scfile.structures.content import ModelContent
from scfile.structures.models import Feature


def test_animation() -> None:
    assert Options(model={"animation": True}).model.skeleton_enabled
    assert Options(model={"animation": True}).model.features == (Feature.SKELETON, Feature.ANIMATION)


def test_targets() -> None:
    assert Options().targets == DEFAULT_TARGETS
    assert Options(model={"skeleton": True}).targets[ModelContent] is FileFormat.GLB
    assert Options(targets={ModelContent: FileFormat.FBX}).targets[ModelContent] is FileFormat.FBX


def test_model_config() -> None:
    assert get_type_hints(ModelConfig) == {field.name: field.type for field in fields(ModelOptions)}


def test_region_config() -> None:
    assert get_type_hints(RegionConfig) == {field.name: field.type for field in fields(RegionOptions)}


def test_copy() -> None:
    options = Options(model={"skeleton": True}, region={"raw_blocks": True})
    copied = options.copy()
    copied.model.animation = True
    copied.region.full_chunk = True

    assert options.model.animation is False
    assert options.region.full_chunk is False
    assert copied.model.animation is True
    assert copied.region.full_chunk is True
