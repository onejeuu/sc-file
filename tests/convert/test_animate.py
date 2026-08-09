from collections.abc import Callable
from pathlib import Path

import pytest

from scfile import types
from scfile.convert import animate
from scfile.options import Options


type Operation = Callable[..., types.ResultPath]


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
