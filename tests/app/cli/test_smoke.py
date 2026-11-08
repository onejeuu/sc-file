from pathlib import Path

import pytest
from click.testing import CliRunner

from scfile.app.cli import scfile
from tests.fixtures import ASSETS


FORMATS = ASSETS / "formats"
DOCUMENT_SOURCE = FORMATS / "document" / "source" / "document.nbt"
MODEL_SOURCE = FORMATS / "models" / "source" / "model_v15.mcsb"
ANIMATION_SOURCE = FORMATS / "models" / "source" / "animation.mcvd"


@pytest.mark.parametrize(
    "args",
    [
        ["--help"],
        ["--version"],
        ["convert", "--help"],
        ["animate", "--help"],
        ["animate", "arms", "--help"],
        ["animate", "face", "--help"],
        ["animate", "body", "--help"],
        ["mapcache", "--help"],
        ["maptiles", "--help"],
    ],
)
def test_cli_help(args: list[str]) -> None:
    result = CliRunner().invoke(scfile, args)

    assert result.exit_code == 0, result.output
    assert result.output


def test_convert_writes_requested_output(tmp_path: Path) -> None:
    output = tmp_path / "output"

    result = CliRunner().invoke(scfile, ["convert", str(DOCUMENT_SOURCE), "-O", str(output), "-W", "1"])

    assert result.exit_code == 0, result.output
    assert any(path.is_file() for path in output.rglob("*"))


def test_animate_writes_requested_output(tmp_path: Path) -> None:
    output = tmp_path / "animation.glb"

    result = CliRunner().invoke(
        scfile,
        ["animate", "arms", str(ANIMATION_SOURCE), str(MODEL_SOURCE), "-O", str(output)],
    )

    assert result.exit_code == 0, result.output
    assert output.is_file()
    assert output.stat().st_size > 0


@pytest.mark.parametrize(
    "args",
    [
        ["convert"],
        ["convert", str(DOCUMENT_SOURCE), "-I", "unknown"],
        ["convert", str(DOCUMENT_SOURCE), "--layout", "unknown"],
        ["animate"],
        ["animate", "arms"],
        ["mapcache"],
    ],
)
def test_cli_validation(args: list[str]) -> None:
    result = CliRunner().invoke(scfile, args)

    assert result.exit_code == 2
    assert result.output
