import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scfile.__main__ import main
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


def test_main_no_gui():
    testargs = ["scfile"]
    with patch.object(sys, "argv", testargs):
        with patch("scfile.__main__._run_gui", side_effect=SystemExit(1)):
            with pytest.raises(SystemExit):
                main()


def test_run_gui_import_error():
    with patch.dict(sys.modules):
        sys.modules.pop("scfile.gui", None)
        sys.modules.pop("scfile.gui.window", None)
        with patch("builtins.input", return_value=""):
            with pytest.raises(SystemExit):
                from scfile.__main__ import _run_gui

                _run_gui()
