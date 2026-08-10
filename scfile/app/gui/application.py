"""Graphical application startup."""

import sys
from signal import SIGINT, signal

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from .window import MainWindow


def run() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    signal(SIGINT, lambda *_: QTimer.singleShot(0, window.close))

    signal_timer = QTimer()
    signal_timer.timeout.connect(lambda: None)
    signal_timer.start(100)

    window.show()
    return app.exec()
