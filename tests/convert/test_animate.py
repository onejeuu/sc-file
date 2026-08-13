from collections.abc import Callable
from pathlib import Path

import pytest

from scfile import types
from scfile.convert import animate
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
def test_animation_skips_existing_output(
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
def test_animation_export(
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
