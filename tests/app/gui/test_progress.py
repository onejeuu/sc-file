from PySide6.QtWidgets import QApplication

from scfile.app.gui.widgets.progress import ProgressButton


def test_progress_button(qapp: QApplication) -> None:
    button = ProgressButton("CONVERT")

    button.start(12)
    button.advance()
    assert button.running

    button.finish()
    assert not button.running

    button.deleteLater()
    qapp.processEvents()
