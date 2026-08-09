from pathlib import Path

from scfile.convert.animate import arms, body


ASSETS = Path(__file__).parents[1] / "assets"
SOURCE = ASSETS / "formats" / "models" / "source"
EXPECTED = ASSETS / "operations" / "animate"


def test_arms(
    tmp_path: Path,
) -> None:
    output = tmp_path / "arms.glb"
    assert arms(SOURCE / "animation.mcvd", SOURCE / "model_v15.mcsb", output=output) == output
    assert output.read_bytes() == (EXPECTED / output.name).read_bytes()


def test_body(
    tmp_path: Path,
) -> None:
    output = tmp_path / "body.glb"
    assert body(SOURCE / "library.mcal", SOURCE / "model_v15.mcsb", output=output) == output
    assert output.read_bytes() == (EXPECTED / output.name).read_bytes()
