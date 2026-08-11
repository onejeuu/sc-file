import time
from pathlib import Path

from PySide6.QtWidgets import QApplication

from scfile.app.gui.workers.counter import FileCounter


def test_counter(qapp: QApplication, tmp_path: Path) -> None:
    (tmp_path / "first.mic").touch()
    (tmp_path / "second.mic").touch()
    (tmp_path / "other.ol").touch()

    counter = FileCounter()
    counter.refresh((str(tmp_path),), (".mic",))

    limit = time.monotonic() + 2
    while counter.busy and time.monotonic() < limit:
        qapp.processEvents()
        time.sleep(0.01)

    assert not counter.busy
    assert counter.count == 2
    counter.stop()
    counter.deleteLater()
    qapp.processEvents()
