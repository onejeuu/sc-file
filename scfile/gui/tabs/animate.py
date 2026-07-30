from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from scfile.gui import workers
from scfile.gui.shared import strings
from scfile.gui.shared.styles import Styles
from scfile.gui.widgets.path import PathInputWidget
from scfile.gui.widgets.warnings import WarningsWidget
from scfile.gui.workers.animate import AnimateWorker
from scfile.gui.workers.base import Worker
from scfile.gui.workers.lipsync import LipsyncWorker


class AnimateTab(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: Worker | None = None
        self._worker_thread: QThread | None = None
        self._setup_warnings()
        self._build_ui()

    def _setup_warnings(self) -> None:
        self.warnings = WarningsWidget()
        self.warnings.add_rule(self._warn_not_fp_animation)

    def _warn_not_fp_animation(self) -> str | None:
        if not self.fp_mode.isChecked():
            return None

        animation = Path(self.animation.text().strip())
        stem = animation.stem.lower()
        if animation.suffix.lower() == ".mcvd" and ("fp_" not in stem or "wpn_" not in stem):
            return strings.get("warning.animate.not_fp")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        self._add_modes(layout)
        self.animation = self._add_path(
            layout,
            label=strings.get("label.animate.animation"),
            caption=strings.get("dialog.animate.animation"),
            file_filter="MCVD (*.mcvd)",
        )
        layout.addWidget(self.warnings)

        self.model_label, self.model = self._create_path(
            label=strings.get("label.animate.model"),
            caption=strings.get("dialog.animate.model"),
            file_filter="MCSB (*.mcsb)",
        )
        layout.addWidget(self.model_label)
        layout.addWidget(self.model)

        self.additional_label, self.additional_model = self._create_path(
            label=strings.get("label.animate.additional"),
            caption=strings.get("dialog.animate.additional"),
            file_filter="MCSB (*.mcsb)",
            placeholder=strings.get("placeholder.optional"),
        )
        layout.addWidget(self.additional_label)
        layout.addWidget(self.additional_model)

        output_label = QLabel(strings.get("label.animate.output"))
        output_label.setStyleSheet(Styles.LABEL)
        self.output = PathInputWidget(
            placeholder=strings.get("placeholder.animate.output"),
            caption=strings.get("dialog.animate.output"),
            mode="save",
            file_filter="GLB (*.glb)",
            default_suffix=".glb",
        )

        layout.addWidget(output_label)
        layout.addWidget(self.output)
        layout.addStretch()

        self.export = QPushButton(strings.get("button.animate"))
        self.export.setFixedHeight(50)
        self.export.setStyleSheet(Styles.BUTTON_ACCENT)
        self.export.clicked.connect(self._animate)
        layout.addWidget(self.export)

        for path in (self.animation, self.model, self.additional_model, self.output):
            path.changed.connect(self._sync_ui)

        self._sync_ui()

    def _add_modes(self, layout: QVBoxLayout) -> None:
        widget = QWidget()
        widget.setStyleSheet(Styles.TOGGLE_GROUP)
        modes = QHBoxLayout(widget)
        modes.setContentsMargins(0, 0, 0, 0)
        modes.setSpacing(0)

        self.fp_mode = QPushButton(strings.get("mode.animate.fp"))
        self.lipsync_mode = QPushButton(strings.get("mode.animate.lipsync"))
        self.mode = QButtonGroup(self)
        self.mode.setExclusive(True)

        for index, button in enumerate((self.fp_mode, self.lipsync_mode)):
            button.setCheckable(True)
            button.setStyleSheet(Styles.TOGGLE_ITEM)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            modes.addWidget(button)
            self.mode.addButton(button, index)

        self.fp_mode.setChecked(True)
        self.mode.idClicked.connect(self._change_mode)
        layout.addWidget(widget)

    def _change_mode(self, _: int) -> None:
        self._sync_ui()

    def _add_path(
        self,
        layout: QVBoxLayout,
        label: str,
        caption: str,
        file_filter: str,
        placeholder: str | None = None,
    ) -> PathInputWidget:
        title, path = self._create_path(label, caption, file_filter, placeholder)
        layout.addWidget(title)
        layout.addWidget(path)
        return path

    @staticmethod
    def _create_path(
        label: str,
        caption: str,
        file_filter: str,
        placeholder: str | None = None,
    ) -> tuple[QLabel, PathInputWidget]:
        title = QLabel(label)
        title.setStyleSheet(Styles.LABEL)
        path = PathInputWidget(
            placeholder=placeholder or strings.get("placeholder.path"),
            caption=caption,
            mode="open",
            file_filter=file_filter,
        )
        return title, path

    @staticmethod
    def _valid_file(value: str, suffix: str) -> bool:
        path = Path(value.strip())
        return bool(value.strip()) and path.is_file() and path.suffix.lower() == suffix

    def _sync_ui(self) -> None:
        is_fp = self.fp_mode.isChecked()
        animation = self.animation.text().strip()
        model = self.model.text().strip()
        additional = self.additional_model.text().strip()
        output = self.output.text().strip()

        self.model_label.setText(strings.get("label.animate.model" if is_fp else "label.animate.head"))
        self.model.caption = strings.get("dialog.animate.model" if is_fp else "dialog.animate.head")
        self.additional_label.setVisible(is_fp)
        self.additional_model.setVisible(is_fp)

        if animation:
            self.output.initial_path = Path(animation).with_suffix(".glb").name

        self.warnings.update_state()

        animation_ok = self._valid_file(animation, ".mcvd")
        model_ok = self._valid_file(model, ".mcsb")
        additional_ok = not is_fp or not additional or self._valid_file(additional, ".mcsb")
        output_ok = Path(output).suffix.lower() == ".glb"
        ready = animation_ok and model_ok and additional_ok and output_ok and self._worker is None

        tooltip = {
            output_ok: "tooltip.animate.invalid.output",
            additional_ok: "tooltip.animate.invalid.additional",
            model_ok: "tooltip.animate.invalid.model",
            animation_ok: "tooltip.animate.invalid.animation",
        }.get(False, "")

        self.export.setEnabled(ready)
        self.export.setToolTip(strings.get(tooltip))
        self.export.setCursor(Qt.CursorShape.PointingHandCursor if ready else Qt.CursorShape.ForbiddenCursor)

    def _animate(self) -> None:
        animation = Path(self.animation.text().strip())
        model = Path(self.model.text().strip())
        output = Path(self.output.text().strip())

        if self.fp_mode.isChecked():
            models = [model]
            if additional := self.additional_model.text().strip():
                models.append(Path(additional))

            self._worker = AnimateWorker(
                animation=animation,
                models=models,
                output=output,
            )
        else:
            self._worker = LipsyncWorker(
                animation=animation,
                model=model,
                output=output,
            )
        self._worker_thread = workers.execute(self._worker, on_done=self._on_finish)
        self._sync_ui()

    def _on_finish(self) -> None:
        self._worker = None
        self._worker_thread = None
        self._sync_ui()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._worker and self._worker_thread:
            workers.stop(self._worker, self._worker_thread)

        super().closeEvent(event)
