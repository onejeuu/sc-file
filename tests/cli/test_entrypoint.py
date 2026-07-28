import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scfile.__main__ import _default_command, main
from scfile.enums import CliCommand
from tests.conftest import ASSETS


def test_main_help():
    testargs = ["scfile", "--help"]
    with patch.object(sys, "argv", testargs):
        with pytest.raises(SystemExit):
            main()


def test_main_version():
    testargs = ["scfile", "--version"]
    with patch.object(sys, "argv", testargs):
        with pytest.raises(SystemExit):
            main()


def test_main_convert():
    testargs = ["scfile", "convert"]
    with patch.object(sys, "argv", testargs):
        with pytest.raises(SystemExit):
            main()


def test_main_mapcache():
    testargs = ["scfile", "mapcache"]
    with patch.object(sys, "argv", testargs):
        with pytest.raises(SystemExit):
            main()


def test_main_mapcache_keyword():
    testargs = ["scfile", "path/to/map_cache/5.0"]
    with patch.object(sys, "argv", testargs):
        with pytest.raises(SystemExit):
            main()


def test_main_implicit_convert(temp: Path):
    src = str(ASSETS / "cli/model_v12.mcsb")
    testargs = ["scfile", src, "-O", str(temp)]
    with patch.object(sys, "argv", testargs):
        with pytest.raises(SystemExit):
            main()
    assert (temp / "model_v12.obj").exists()


@pytest.mark.parametrize(
    "models",
    [
        ["model.mcsb"],
        ["hands.mcsb", "weapon.mcsb"],
    ],
)
def test_implicit_animate(models: list[str]):
    assert _default_command(["wpn_fp_animation.mcvd", *models]) == CliCommand.ANIMATE
def test_many_models_implicit_convert():
    models = [f"model_{index}.mcsb" for index in range(3)]
    assert _default_command(["animation.mcvd", *models]) == CliCommand.CONVERT


def test_mixed_sources_implicit_convert():
    assert _default_command(["animation.mcvd", "model.mcsb", "texture.ol"]) == CliCommand.CONVERT


def test_main_no_args():
    testargs = ["scfile"]
    with patch.object(sys, "argv", testargs):
        with patch.dict(sys.modules, {"scfile.gui.window": MagicMock()}):
            with pytest.raises(SystemExit):
                main()


def test_main_keyboard_interrupt():
    testargs = ["scfile", "--help"]
    with patch.object(sys, "argv", testargs):
        with patch("scfile.__main__.scfile", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit):
                main()
