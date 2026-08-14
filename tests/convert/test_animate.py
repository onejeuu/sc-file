from collections.abc import Callable
from pathlib import Path

import pytest

from scfile import types
from scfile.convert import animate
from scfile.options import Options
from scfile.structures.content import ModelContent
from scfile.structures.models import AnimationClip


type Operation = Callable[..., types.ResultPath]


ASSETS = Path(__file__).parents[1] / "assets"
SOURCE = ASSETS / "formats" / "models" / "source"
EXPECTED = ASSETS / "convert" / "animate"


@pytest.mark.parametrize(
    ("operation", "suffix"),
    [
        (animate.arms, ".mcvd"),
        (animate.body, ".mcal"),
        (animate.face, ".mcvd"),
    ],
)
def test_skip(
    operation: Operation,
    suffix: str,
    tmp_path: Path,
) -> None:
    source = tmp_path / f"animation{suffix}"
    model = tmp_path / "model.mcsb"
    output = tmp_path / "animation.glb"
    source.write_bytes(b"")
    model.write_bytes(b"")
    output.write_bytes(b"existing")

    result = operation(source, model, options=Options(on_conflict="skip"))

    assert result is None
    assert output.read_bytes() == b"existing"


@pytest.mark.parametrize(
    ("operation", "animation", "model", "expected"),
    (
        (animate.arms, "animation.mcvd", "model_v15.mcsb", "arms.glb"),
        (animate.body, "library.mcal", "model_v15.mcsb", "body.glb"),
    ),
)
def test_export(
    operation: Operation,
    animation: str,
    model: str,
    expected: str,
    tmp_path: Path,
) -> None:
    output = tmp_path / expected

    result = operation(SOURCE / animation, SOURCE / model, output=output)

    assert result == output
    assert output.read_bytes() == (EXPECTED / expected).read_bytes()


def test_arms_hands(tmp_path: Path) -> None:
    output = tmp_path / "arms.glb"

    result = animate.arms(
        SOURCE / "animation.mcvd",
        SOURCE / "model_v15.mcsb",
        SOURCE / "model_v15.mcsb",
        output=output,
    )

    assert result == output


def test_clips() -> None:
    clips = [
        AnimationClip(name="idle", frames=60),
        AnimationClip(name="idle_copy", frames=60),
        AnimationClip(name="pose", frames=2),
        AnimationClip(name="idle_cluster_0", frames=60),
        AnimationClip(name="idle_layer", frames=60),
        AnimationClip(name="idle_turn_l", frames=16),
        AnimationClip(name="idle_look_l", frames=16),
        AnimationClip(name="idle_aim_point_l", frames=16),
        AnimationClip(name="idle_landing", frames=16),
        AnimationClip(name="idle_turn_l", frames=17),
        AnimationClip(name="idle_look_l", frames=18),
        AnimationClip(name="idle_aim_point_l", frames=19),
        AnimationClip(name="idle_landing", frames=20),
    ]

    library = ModelContent()
    library.scene.animation.clips = clips
    result = animate._filtered_library(library)

    assert [clip.name for clip in result.scene.animation.clips] == [clip.name for clip in clips[0:1] + clips[9:]]
