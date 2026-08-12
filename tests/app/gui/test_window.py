from PySide6.QtWidgets import QApplication

from scfile.app.gui.window import MainWindow


def test_window(qapp: QApplication) -> None:
    window = MainWindow()
    window.show()
    qapp.processEvents()

    assert window.stack.count() == 4

    window.close()
    qapp.processEvents()
    assert not window.isVisible()
