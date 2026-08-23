from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest

from scfile import types
from scfile.content.models import AnimationClip
from scfile.convert import animate
from scfile.enums import OnConflict
from scfile.options import Options


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

    result = operation(source, model, options=Options(on_conflict=OnConflict.SKIP))

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


def test_arms_hands_only(tmp_path: Path) -> None:
    output = tmp_path / "hands.glb"

    result = animate.arms(
        SOURCE / "animation.mcvd",
        hands=SOURCE / "model_v15.mcsb",
        output=output,
    )

    assert result == output


def test_clips() -> None:
    def clip(
        name: str,
        frames: int,
        *,
        moving: bool = False,
        offset: float = 1.0,
    ) -> AnimationClip:
        translations = np.zeros((frames, 1, 3), dtype=np.float32)
        rotations = np.zeros((frames, 1, 4), dtype=np.float32)
        rotations[:, :, 3] = 1.0

        if moving:
            translations[-1, 0, 0] = offset

        return AnimationClip(name=name, frames=frames, translations=translations, rotations=rotations)

    clips = [
        clip("idle", 60, moving=True),
        clip("idle_copy", 60, moving=True),
        clip("pose", 2),
        clip("idle_cluster_0", 60, moving=True),
        clip("idle_layer", 60, moving=True),
        clip("idle_turn_l", 16),
        clip("idle_turn_l", 2, moving=True, offset=2.0),
        clip("idle_look_l", 16),
        clip("idle_look_l", 2, moving=True, offset=3.0),
        clip("idle_aim_point_l", 16),
        clip("idle_landing", 16),
        clip("short_landing", 2, moving=True, offset=4.0),
    ]

    result = animate._filter_clips(clips)

    assert [clip.name for clip in result] == ["idle", "pose", "idle_turn_l", "idle_look_l", "idle_landing", "short_landing"]
