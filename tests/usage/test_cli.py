from pathlib import Path
from typing import Iterator, Optional, Sequence
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from scfile import UserOptions
from scfile.cli import scfile
from scfile.enums import FileFormat


@pytest.fixture
def cli() -> CliRunner:
    return CliRunner()


@pytest.fixture
def mock_convert() -> Iterator[MagicMock]:
    with patch("scfile.convert.auto") as mock:
        yield mock


@pytest.fixture
def mock_cli_utils() -> Iterator[MagicMock]:
    with patch("scfile.cli.utils") as mock:
        yield mock


def invoke_scfile_command(
    cli: CliRunner,
    source: Path,
    output: Path,
    mock_convert: MagicMock,
    args: Optional[Sequence[str]] = None,
    options: Optional[UserOptions] = None,
):
    base_args = [str(source), "--output", str(output)]
    if args:
        base_args.extend(args)

    result = cli.invoke(scfile, base_args)

    assert result.exit_code == 0
    expected_options = options or UserOptions()
    mock_convert.assert_called_with(source=source, output=output, options=expected_options)


@pytest.mark.parametrize(
    "name",
    ["model.mcsa", "texture.ol", "cubemap.ol", "image.mic"],
)
def test_convert_files(cli: CliRunner, assets: Path, temp: Path, mock_convert: MagicMock, name: str):
    invoke_scfile_command(cli, assets / name, temp, mock_convert)


@pytest.mark.parametrize(
    "name",
    ["model.mcsa", "texture.ol", "cubemap.ol", "image.mic"],
)
def test_output_to_subdirectory(cli: CliRunner, assets: Path, temp: Path, mock_convert: MagicMock, name: str):
    invoke_scfile_command(cli, assets / name, temp / "foo" / "bar", mock_convert)


def test_model_export_formats(cli: CliRunner, assets: Path, temp: Path, mock_convert: MagicMock):
    path = assets / "model.mcsa"
    invoke_scfile_command(
        cli,
        path,
        temp,
        mock_convert,
        args=["-F", "dae", "-F", "ms3d"],
        options=UserOptions(model_formats=(FileFormat.DAE, FileFormat.MS3D)),
    )


def test_model_skeleton(cli: CliRunner, assets: Path, temp: Path, mock_convert: MagicMock):
    path = assets / "model.mcsa"
    invoke_scfile_command(
        cli,
        path,
        temp,
        mock_convert,
        args=["--skeleton"],
        options=UserOptions(parse_skeleton=True),
    )


def test_model_animation(cli: CliRunner, assets: Path, temp: Path, mock_convert: MagicMock):
    path = assets / "model.mcsa"
    invoke_scfile_command(
        cli,
        path,
        temp,
        mock_convert,
        args=["--skeleton", "--animation"],
        options=UserOptions(parse_skeleton=True, parse_animation=True),
    )
