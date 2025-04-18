from unittest.mock import patch

import pytest

from scfile.cli.scfile import scfile


@pytest.fixture
def mock_convert_auto():
    with patch("scfile.convert.auto.auto") as mock:
        yield mock


@pytest.fixture
def mock_paths_to_files_map():
    with patch("scfile.cli.scfile.utils.paths_to_files_map", return_value={}) as mock:
        yield mock


@pytest.fixture
def runner():
    from click.testing import CliRunner

    return CliRunner()


def test_scfile_no_args(runner, mock_convert_auto, mock_paths_to_files_map):
    result = runner.invoke(scfile, [])
    assert result.exit_code == 0
    mock_convert_auto.assert_not_called()


def test_scfile_no_supported_files(runner, mock_convert_auto, mock_paths_to_files_map):
    mock_paths_to_files_map.return_value = {}
    result = runner.invoke(scfile, ["path/to/nonexistent.file"])
    assert result.exit_code == 2
    mock_convert_auto.assert_not_called()


def test_scfile_with_invalid_model_formats(runner, mock_convert_auto, mock_paths_to_files_map):
    result = runner.invoke(scfile, ["path/to/file.mcsa", "--model-formats", ".invalid", ".mcsa"])
    assert result.exit_code != 0
    mock_convert_auto.assert_not_called()


def test_scfile_with_invalid_output_path(runner, mock_convert_auto, mock_paths_to_files_map):
    result = runner.invoke(scfile, ["path/to/file.mcsa", "--output", "/invalid/path/to/output"])
    assert result.exit_code != 0
    mock_convert_auto.assert_not_called()
