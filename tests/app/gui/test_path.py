from pathlib import Path

from PySide6.QtCore import QEvent, QMimeData, Qt, QUrl
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

from scfile.app.gui.widgets.path import PathInputWidget


def test_path_is_normalized_on_every_input(qapp: QApplication) -> None:
    widget = PathInputWidget("path", "path")
    values: list[str] = []
    widget.text_changed.connect(values.append)

    widget.value = r"C:\game\modassets\assets\file.mcvd"
    assert widget.value == "C:/game/modassets/assets/file.mcvd"
    assert widget.line_edit.text() == "C:/game/modassets/assets/file.mcvd"
    assert values == ["C:/game/modassets/assets/file.mcvd"]

    widget.line_edit.insert(r"\nested")
    assert widget.value.endswith("/nested")
    assert values[-1].endswith("/nested")

    data = QMimeData()
    data.setText(r"\from-clipboard")
    widget.line_edit.insertFromMimeData(data)
    assert widget.value.endswith("/nested/from-clipboard")
    assert all("\\" not in value for value in values)

    widget.initial_path = r"C:\game\assets"
    assert widget.initial_path == "C:/game/assets"

    widget.deleteLater()
    qapp.processEvents()


def test_file_paste_uses_local_path(qapp: QApplication, tmp_path: Path) -> None:
    widget = PathInputWidget("path", "path")
    widget.value = "old/path.mcvd"
    data = QMimeData()
    data.setUrls([QUrl.fromLocalFile(str(tmp_path / "file.mcvd"))])
    qapp.clipboard().setMimeData(data)

    event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_V, Qt.KeyboardModifier.ControlModifier)
    widget.line_edit.keyPressEvent(event)

    assert widget.value == (tmp_path / "file.mcvd").as_posix()
    assert not widget.value.startswith("file:")

    data = QMimeData()
    data.setText(r"\relative")
    qapp.clipboard().setMimeData(data)

    event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_V, Qt.KeyboardModifier.ControlModifier)
    widget.line_edit.keyPressEvent(event)

    assert widget.value == f"{tmp_path.as_posix()}/file.mcvd/relative"

    qapp.clipboard().clear()
    widget.deleteLater()
    qapp.processEvents()
