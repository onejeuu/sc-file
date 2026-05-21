import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scfile.__main__ import main


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


def test_main_implicit_convert(assets: Path, temp: Path):
    src = str(assets / "cli" / "model_v12.mcsb")
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
