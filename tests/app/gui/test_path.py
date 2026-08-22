from PySide6.QtWidgets import QApplication

from scfile.app.gui.widgets.path import PathInputWidget


def test_path_is_normalized_everywhere(qapp: QApplication) -> None:
    widget = PathInputWidget("path", "path")

    widget.value = r"C:\game\modassets\assets\file.mcvd"
    assert widget.value == "C:/game/modassets/assets/file.mcvd"
    assert widget.line_edit.text() == "C:/game/modassets/assets/file.mcvd"

    widget.line_edit.insert(r"\nested")
    assert widget.value.endswith("/nested")

    widget.as_posix = False
    widget.value = r"C:\game\file.mcvd"
    assert widget.value == r"C:\game\file.mcvd"

    widget.as_posix = True
    assert widget.value == "C:/game/file.mcvd"

    widget.initial_path = r"C:\game\assets"
    assert widget.initial_path == "C:/game/assets"

    widget.deleteLater()
    qapp.processEvents()
