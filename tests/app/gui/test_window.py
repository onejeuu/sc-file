from PySide6.QtWidgets import QApplication

from scfile.app.gui.window import MainWindow


def test_window_opens_and_closes(qapp: QApplication) -> None:
    window = MainWindow()
    window.show()
    qapp.processEvents()

    window.close()
    qapp.processEvents()
    assert not window.isVisible()
