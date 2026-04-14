import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from scfile import __version__

from . import utils
from .tabs.convert import ConverterTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowIcon(QIcon(str(utils.get_resource("assets/scfile.ico"))))
        self.setWindowTitle(f"scfile {__version__}")
        self.resize(1000, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.content_stack = QStackedWidget()

        self.converter_tab = ConverterTab()
        self.content_stack.addWidget(self.converter_tab)

        self.main_layout.addWidget(self.content_stack)


def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
