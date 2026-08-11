import sys
from signal import SIGINT, signal

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from .window import MainWindow


def run() -> int:
    # Initialize Qt
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Build the application window
    window = MainWindow()

    # Route Ctrl+C through the event loop
    signal(SIGINT, lambda *_: QTimer.singleShot(0, window.close))

    # Keep Python signals active while Qt runs
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    # Show the window and run the event loop
    window.show()
    return app.exec()
