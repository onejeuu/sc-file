from PySide6.QtWidgets import QApplication

from scfile.app.gui.tasks import TaskWidget
from scfile.app.gui.window import MainWindow


def test_window(qapp: QApplication) -> None:
    window = MainWindow()
    window.show()
    qapp.processEvents()

    assert window.footer.findChild(TaskWidget) is not None
    assert window.stack.count() == 4

    window.close()
    qapp.processEvents()
    assert not window.isVisible()
