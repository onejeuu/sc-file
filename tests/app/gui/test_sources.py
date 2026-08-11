from pathlib import Path

from scfile.app.gui.widgets.sources import _display_path


def test_display_path() -> None:
    source = Path.home() / "scfile" / "source"

    assert _display_path(source) == "~/scfile/source"
