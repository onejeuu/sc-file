import time
from pathlib import Path

from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication

from scfile.app.gui.workers.counter import FileCounter


def test_counter(qapp: QApplication, tmp_path: Path) -> None:
    (tmp_path / "first.mic").touch()
    (tmp_path / "second.mic").touch()
    (tmp_path / "other.ol").touch()

    counter = FileCounter()
    counter.refresh((str(tmp_path),), (".mic",))
    deadline = time.monotonic() + 2
    while counter.busy and time.monotonic() < deadline:
        qapp.processEvents()
        QThread.msleep(10)

    assert not counter.busy
    assert counter.count == 2
    counter.stop()
    counter.deleteLater()
    qapp.processEvents()
