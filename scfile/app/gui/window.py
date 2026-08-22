from pathlib import Path
from typing import override

from PySide6.QtCore import QSize
from PySide6.QtGui import QCloseEvent, QIcon, Qt
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from scfile.app import files, game
from scfile.app.consts import TITLE
from scfile.app.feedback import TaskFeedback
from scfile.app.gui import strings
from scfile.app.gui.settings import Store
from scfile.app.gui.styles import Styles
from scfile.app.gui.tabs.animate import AnimateTab
from scfile.app.gui.tabs.convert import ConvertTab
from scfile.app.gui.tabs.mapcache import MapCacheTab
from scfile.app.gui.tabs.settings import SettingsTab
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui.widgets.footer import FooterWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._closing = False
        self._stopped = False

        self.store = Store()
        self.settings = self.store.load()
        self._resolve_game_root()

        self.tasks = TaskManager(self)
        self.feedback = TaskFeedback(self.settings.verbose, timestamps=True)
        self.tasks.reported.connect(self.feedback)
        self.tasks.completed.connect(self.feedback.finish)
        self.tasks.busy_changed.connect(self._task_busy_changed)

        self._build_ui()

    def _resolve_game_root(self) -> None:
        installation = game.resolve(self.settings.game_root or Path.home())
        if installation is None or installation.root == self.settings.game_root:
            return

        self.settings.game_root = installation.root
        self.store.save(self.settings)

    def _build_ui(self) -> None:
        self.setWindowIcon(QIcon(str(files.resource("assets/app.icon.ico"))))
        self.setWindowTitle(TITLE)
        self.setStyleSheet(Styles.WINDOW)
        self.resize(1000, 800)

        root = QWidget()
        self.setCentralWidget(root)

        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(Styles.SIDEBAR)
        sidebar.setFixedWidth(54)
        self.sidebar = QVBoxLayout(sidebar)
        self.sidebar.setContentsMargins(0, 16, 0, 16)
        self.sidebar.setSpacing(8)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 4, 0, 0)
        content_layout.setSpacing(0)
        self.stack = QStackedWidget()

        self.footer = FooterWidget()
        content_layout.addWidget(self.stack)
        content_layout.addWidget(self.footer)

        layout.addWidget(sidebar)
        layout.addWidget(content)

        self.navigation = QButtonGroup(self)
        self.navigation.setExclusive(True)
        self.navigation.idClicked.connect(self.stack.setCurrentIndex)

        self.convert = ConvertTab(self.tasks, self.settings)
        self.convert.error.connect(self.feedback)
        self.convert.settings_changed.connect(self._save_settings)
        self._add_tab(self.convert, "tab.convert", "assets/tab.convert.png")

        self.animate = AnimateTab(self.tasks, self.settings)
        self._add_tab(self.animate, "tab.animate", "assets/tab.animate.png")

        self.mapcache = MapCacheTab(self.tasks, self.settings)
        self._add_tab(self.mapcache, "tab.mapcache", "assets/tab.mapcache.png")
        self.sidebar.addStretch()

        self.settings_tab = SettingsTab(self.settings)
        self.settings_tab.changed.connect(self._save_settings)
        self.settings_tab.game_root_changed.connect(self.mapcache.apply_game_root)
        self.settings_tab.path_resolution_changed.connect(self.mapcache.apply_path_resolution)
        self.settings_tab.path_resolution_changed.connect(self.animate.apply_path_resolution)
        self.settings_tab.verbose_changed.connect(self.feedback.set_verbose)
        self.settings_tab.export_path_changed.connect(self.convert.apply_export_path)
        self.settings_tab.export_path_changed.connect(self.animate.apply_export_path)
        self._add_tab(self.settings_tab, "tab.settings", "assets/tab.settings.png")

        self.navigation.buttons()[0].setChecked(True)
        self.stack.setCurrentIndex(0)

    def _add_tab(self, widget: QWidget, title: str, icon: str) -> None:
        index = self.stack.addWidget(widget)
        button = QPushButton()
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(Styles.SIDEBAR_ITEM)
        button.setToolTip(strings.get(title))
        button.setIcon(QIcon(str(files.resource(icon))))
        button.setIconSize(QSize(20, 20))

        self.sidebar.addWidget(button)
        self.navigation.addButton(button, index)

    def _save_settings(self) -> None:
        self.store.save(self.settings)

    def _task_busy_changed(self, busy: bool) -> None:
        if self._closing and not busy:
            self._shutdown()
            QApplication.quit()

    def _shutdown(self) -> None:
        if self._stopped:
            return

        self._stopped = True
        self.convert.stop()
        self.mapcache.stop()
        self.footer.stop()

    @override
    def closeEvent(self, event: QCloseEvent) -> None:
        if self.tasks.busy:
            self._closing = True
            self.tasks.cancel()
            self.hide()
            event.ignore()
            return

        self._shutdown()
        event.accept()
