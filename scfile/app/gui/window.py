from pathlib import Path
from typing import override

from PySide6.QtCore import QSize
from PySide6.QtGui import QCloseEvent, QColor, QIcon, QPainter, QPixmap, QResizeEvent, Qt
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

from scfile.app import files
from scfile.app.consts import TITLE
from scfile.app.feedback import TaskFeedback
from scfile.app.game import GameRoot
from scfile.app.gui import strings
from scfile.app.gui.settings import Store
from scfile.app.gui.styles import Colors, Styles
from scfile.app.gui.tabs.animate import AnimateTab
from scfile.app.gui.tabs.convert import ConvertTab
from scfile.app.gui.tabs.mapcache import MapCacheTab
from scfile.app.gui.tabs.maptiles import MapTilesTab
from scfile.app.gui.tabs.settings import SettingsTab
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui.widgets.footer import FooterWidget
from scfile.app.gui.widgets.titlebar import TitleBar, WindowResizeFrame
from scfile.app.gui.widgets.updates import VersionWidget
from scfile.app.localization import DOCS_URL


class PageStack(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.currentChanged.connect(self.updateGeometry)

    @override
    def minimumSizeHint(self) -> QSize:
        page = self.currentWidget()
        if page is None:
            return QSize()

        size = page.minimumSizeHint().expandedTo(page.minimumSize())
        size.setHeight(max(size.height(), page.heightForWidth(page.width())))
        return size

    @override
    def sizeHint(self) -> QSize:
        page = self.currentWidget()
        return page.sizeHint() if page else QSize()

    @override
    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.updateGeometry()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._closing = False
        self._stopped = False

        self.store = Store()
        self.settings = self.store.load()
        strings.LANG = self.settings.language
        self._resolve_game_root()

        self.tasks = TaskManager(self)
        self.feedback = TaskFeedback(self.settings.verbose, timestamps=True)
        self.tasks.reported.connect(self.feedback)
        self.tasks.completed.connect(self.feedback.finish)
        self.tasks.busy_changed.connect(self._task_busy_changed)

        self._build_ui()

    def _resolve_game_root(self) -> None:
        game = GameRoot.find(self.settings.game_root or Path.home())
        if game is None or game.root == self.settings.game_root:
            return

        self.settings.game_root = game.root
        self.store.save(self.settings)

    def _build_ui(self) -> None:
        self.setWindowIcon(QIcon(str(files.resource("assets/app.ico"))))
        self.setWindowTitle(TITLE)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(Styles.WINDOW)
        self.resize(1000, 800)

        root = QWidget()
        root.setObjectName("appRoot")
        root.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(1, 1, 1, 1)
        root_layout.setSpacing(0)
        self.title_bar = TitleBar(self)
        root_layout.addWidget(self.title_bar)

        body = QWidget()
        body.setObjectName("windowBody")
        layout = QHBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        root_layout.addWidget(body, 1)

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(Styles.SIDEBAR)
        sidebar.setFixedWidth(56)
        self.sidebar = QVBoxLayout(sidebar)
        self.sidebar.setContentsMargins(0, 12, 0, 12)
        self.sidebar.setSpacing(8)

        content = QWidget()
        content.setObjectName("mainContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        self.stack = PageStack()
        self._help_urls: dict[int, str] = {}

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
        self._add_tab(
            self.convert,
            "tab.convert",
            "assets/tab.convert.png",
            help_url=f"{DOCS_URL}/latest/usage/convert.html",
        )

        self.animate = AnimateTab(self.tasks, self.settings)
        self._add_tab(
            self.animate,
            "tab.animate",
            "assets/tab.animate.png",
            help_url=f"{DOCS_URL}/latest/usage/animate.html",
        )

        self.maptiles = MapTilesTab(self.tasks, self.settings)
        self._add_tab(
            self.maptiles,
            "tab.maptiles",
            "assets/tab.maptiles.png",
            help_url=f"{DOCS_URL}/latest/usage/maptiles.html",
        )

        self.mapcache = MapCacheTab(self.tasks, self.settings)
        self._add_tab(
            self.mapcache,
            "tab.mapcache",
            "assets/tab.mapcache.png",
            help_url=f"{DOCS_URL}/latest/usage/mapcache.html",
        )

        self.sidebar.addStretch()

        self.settings_tab = SettingsTab(self.settings)
        self.settings_tab.changed.connect(self._save_settings)
        self.settings_tab.game_root_changed.connect(self.mapcache.apply_game_root)
        self.settings_tab.game_root_changed.connect(self.animate.apply_game_root)
        self.settings_tab.game_root_changed.connect(self.maptiles.apply_game_root)
        self.settings_tab.path_resolution_changed.connect(self.mapcache.apply_path_resolution)
        self.settings_tab.path_resolution_changed.connect(self.animate.apply_path_resolution)
        self.settings_tab.path_resolution_changed.connect(self.maptiles.apply_path_resolution)
        self.settings_tab.verbose_changed.connect(self.feedback.set_verbose)
        self.settings_tab.export_path_changed.connect(self.convert.apply_export_path)
        self.settings_tab.export_path_changed.connect(self.animate.apply_export_path)
        self.settings_tab.export_path_changed.connect(self.maptiles.apply_export_path)
        self.settings_tab.export_path_changed.connect(self.mapcache.apply_export_path)
        self._add_tab(self.settings_tab, "tab.settings", "assets/tab.settings.png")

        self.version = VersionWidget()
        self.version.setFixedSize(48, 22)
        self.sidebar.addWidget(self.version, 0, Qt.AlignmentFlag.AlignHCenter)

        self.navigation.buttons()[0].setChecked(True)
        self.stack.setCurrentIndex(0)
        self._sync_footer(0)
        self.stack.currentChanged.connect(self._sync_footer)
        root.setFocus(Qt.FocusReason.OtherFocusReason)
        self.resize_frame = WindowResizeFrame(self, root)

    def _add_tab(self, widget: QWidget, title: str, icon: str, help_url: str | None = None) -> None:
        index = self.stack.addWidget(widget)
        if help_url:
            self._help_urls[index] = help_url
        button = QPushButton()
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(Styles.SIDEBAR_ITEM)
        button.setToolTip(strings.get(title))
        button.setIcon(self._sidebar_icon(icon))
        button.setIconSize(QSize(20, 20))

        self.sidebar.addWidget(button)
        self.navigation.addButton(button, index)

    def _sync_footer(self, index: int) -> None:
        self.footer.set_section_help(self._help_urls.get(index))

    def _sidebar_icon(self, resource: str) -> QIcon:
        raw = QPixmap(str(files.resource(resource)))
        icon = QIcon()
        icon.addPixmap(self._tint_icon(raw, Colors.TEXT.value), QIcon.Mode.Normal, QIcon.State.Off)
        icon.addPixmap(self._tint_icon(raw, Colors.ACCENT.value), QIcon.Mode.Normal, QIcon.State.On)
        icon.addPixmap(self._tint_icon(raw, Colors.TEXT_DISABLED.value), QIcon.Mode.Disabled, QIcon.State.Off)
        return icon

    @staticmethod
    def _tint_icon(source: QPixmap, color: QColor) -> QPixmap:
        tinted = QPixmap(source.size())
        tinted.fill(Qt.GlobalColor.transparent)

        painter = QPainter(tinted)
        painter.drawPixmap(0, 0, source)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(tinted.rect(), color)
        painter.end()
        return tinted

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
        self.version.stop()

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
