from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from scfile.app.gui import strings
from scfile.app.gui.styles import Styles
from scfile.app.gui.widgets.combo import ComboBox


class MappingLayersWidget(QWidget):
    """Select one built-in base mapping and ordered JSON overlays."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        base_row = QHBoxLayout()
        base_row.setContentsMargins(0, 0, 0, 0)
        base_label = QLabel(strings.get("label.mapcache.mapping.base"))
        base_label.setStyleSheet(Styles.LABEL)
        base_row.addWidget(base_label)

        self.base = ComboBox()
        self.base.add_named_item("resourcepack", strings.get("option.mapcache.mapping.resourcepack"))
        self.base.add_named_item("vanilla", strings.get("option.mapcache.mapping.vanilla"))
        self.base.setCurrentIndex(0)
        base_row.addWidget(self.base, 1)
        layout.addLayout(base_row)

        self.overlays = QListWidget()
        self.overlays.setStyleSheet(Styles.SOURCES_LIST)
        self.overlays.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.overlays.setMinimumHeight(36)
        self.overlays.setMaximumHeight(108)
        self.overlays.currentRowChanged.connect(self._sync_buttons)
        layout.addWidget(self.overlays)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(6)

        self.add_button = self._button("button.mapcache.mapping.add")
        self.remove_button = self._button("button.mapcache.mapping.remove")
        self.up_button = self._button("button.mapcache.mapping.up")
        self.down_button = self._button("button.mapcache.mapping.down")

        self.add_button.clicked.connect(self._add_overlay)
        self.remove_button.clicked.connect(self._remove_overlay)
        self.up_button.clicked.connect(self._move_up)
        self.down_button.clicked.connect(self._move_down)

        controls.addWidget(self.add_button)
        controls.addWidget(self.remove_button)
        controls.addStretch()
        controls.addWidget(self.up_button)
        controls.addWidget(self.down_button)
        layout.addLayout(controls)

        self._sync_buttons()

    @staticmethod
    def _button(key: str) -> QPushButton:
        button = QPushButton(strings.get(key))
        button.setStyleSheet(Styles.BUTTON)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def values(self) -> tuple[str, ...]:
        """Return mapping specs in application order."""

        base = str(self.base.currentData())
        overlays = tuple(
            str(self.overlays.item(index).data(Qt.ItemDataRole.UserRole))
            for index in range(self.overlays.count())
        )
        return (base, *overlays)

    def _add_overlay(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            strings.get("dialog.mapcache.mapping"),
            str(Path.home()),
            "JSON files (*.json);;All files (*)",
        )
        if not path:
            return

        item = QListWidgetItem(Path(path).name)
        item.setData(Qt.ItemDataRole.UserRole, path)
        item.setToolTip(path)
        self.overlays.addItem(item)
        self.overlays.setCurrentItem(item)

    def _remove_overlay(self) -> None:
        row = self.overlays.currentRow()
        if row < 0:
            return
        self.overlays.takeItem(row)
        self._sync_buttons()

    def _move_up(self) -> None:
        row = self.overlays.currentRow()
        if row <= 0:
            return
        item = self.overlays.takeItem(row)
        self.overlays.insertItem(row - 1, item)
        self.overlays.setCurrentRow(row - 1)

    def _move_down(self) -> None:
        row = self.overlays.currentRow()
        if row < 0 or row >= self.overlays.count() - 1:
            return
        item = self.overlays.takeItem(row)
        self.overlays.insertItem(row + 1, item)
        self.overlays.setCurrentRow(row + 1)

    def _sync_buttons(self, _: int = -1) -> None:
        row = self.overlays.currentRow()
        count = self.overlays.count()
        self.overlays.setFixedHeight(max(36, min(count, 3) * 36))
        self.remove_button.setEnabled(row >= 0)
        self.up_button.setEnabled(row > 0)
        self.down_button.setEnabled(0 <= row < count - 1)
