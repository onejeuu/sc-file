from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from scfile.app.gui.settings import Settings
from scfile.app.gui.tabs.mapcache import MapCacheTab
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui.threads import RequestTokens
from scfile.app.gui.workers.mapcache import Scanner


def test_default_output(qapp: QApplication, tmp_path: Path) -> None:
    tab = MapCacheTab(TaskManager(), Settings(export_path=tmp_path / "export"))
    try:
        tab.source.value = ""
        output = tab.output.input.line_edit
        output.clear()
        QTest.keyClick(output, Qt.Key.Key_Backspace)
        assert not tab.output.value

        source = tmp_path / "cache"
        source.mkdir()
        tab.source.value = str(source)
        tab._edit_source(tab.source.value)
        assert Path(tab.output.value) == tmp_path / "export/cache_mca"

        custom = tmp_path / "world/region"
        tab.output.value = str(custom)
        tab._edit_output(tab.output.value)
        tab.apply_export_path(tmp_path / "other")
        tab._edit_source(tab.source.value)
        assert Path(tab.output.value) == custom

        output.clear()
        tab._edit_output("")
        QTest.keyClick(output, Qt.Key.Key_Delete)
        assert Path(tab.output.value) == tmp_path / "other/cache_mca"
        assert tab.output not in tab.touched
        assert tab.world is None

        tab.apply_export_path(tmp_path / "new")
        assert Path(tab.output.value) == tmp_path / "new/cache_mca"

        tab.source.value = ""
        tab._edit_source("")
        output.clear()
        QTest.keyClick(output, Qt.Key.Key_Backspace)
        assert not tab.output.value
    finally:
        tab.stop()
        tab.deleteLater()
        qapp.processEvents()


@pytest.mark.parametrize(
    ("target", "overlap"),
    (("r.1.-2.mca", True), ("r.0.0.mca", False)),
)
def test_overlap(tmp_path: Path, target: str, overlap: bool) -> None:
    source = tmp_path / "cache"
    source.mkdir()
    (source / "reg.1.-2.mdat").write_bytes(b"data")
    output = tmp_path / "region"
    output.mkdir()
    (output / target).touch()

    requests = RequestTokens()
    request = requests.next()
    scanner = Scanner(requests)
    results = []
    scanner.scanned.connect(lambda *result: results.append(result))

    scanner.scan(request, str(source), str(output))

    assert results == [(request, 1, 1, overlap, None)]
