from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from scfile.gui import workers
from scfile.gui.shared import strings
from scfile.gui.shared.styles import Styles
from scfile.gui.widgets import PathInputWidget
from scfile.gui.workers.animate import AnimateWorker


class AnimateTab(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: AnimateWorker | None = None
        self._worker_thread: QThread | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        self.animation = self._add_path(
            layout,
            label=strings.get("label.animate.animation"),
            caption=strings.get("dialog.animate.animation"),
            file_filter="MCVD (*.mcvd)",
        )
        self.model = self._add_path(
            layout,
            label=strings.get("label.animate.model"),
            caption=strings.get("dialog.animate.model"),
            file_filter="MCSB (*.mcsb)",
        )
        self.additional_model = self._add_path(
            layout,
            label=strings.get("label.animate.additional"),
            caption=strings.get("dialog.animate.additional"),
            file_filter="MCSB (*.mcsb)",
            placeholder=strings.get("placeholder.optional"),
        )

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

    def _add_path(
        self,
        layout: QVBoxLayout,
        label: str,
        caption: str,
        file_filter: str,
        placeholder: str | None = None,
    ) -> PathInputWidget:
        title = QLabel(label)
        title.setStyleSheet(Styles.LABEL)

        path = PathInputWidget(
            placeholder=placeholder or strings.get("placeholder.path"),
            caption=caption,
            mode="open",
            file_filter=file_filter,
        )

        layout.addWidget(title)
        layout.addWidget(path)
        return path

    @staticmethod
    def _valid_file(value: str, suffix: str) -> bool:
        path = Path(value.strip())
        return bool(value.strip()) and path.is_file() and path.suffix.lower() == suffix

    def _sync_ui(self) -> None:
        animation = self.animation.text().strip()
        model = self.model.text().strip()
        additional = self.additional_model.text().strip()
        output = self.output.text().strip()

        is_mcvd = Path(animation).suffix.lower() == ".mcvd"
        self.additional_model.setEnabled(is_mcvd)
        if animation:
            self.output.initial_path = Path(animation).with_suffix(".glb").name

        animation_ok = self._valid_file(animation, ".mcvd")
        model_ok = self._valid_file(model, ".mcsb")
        additional_ok = not additional or self._valid_file(additional, ".mcsb")
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
        models = [Path(self.model.text().strip())]
        if additional := self.additional_model.text().strip():
            models.append(Path(additional))

        output = self.output.text().strip()

        self._worker = AnimateWorker(
            animation=Path(self.animation.text().strip()),
            models=models,
            output=Path(output) if output else None,
        )
        self._worker_thread = workers.execute(self._worker, on_done=self._on_finish)
        self._sync_ui()

    def _on_finish(self) -> None:
        self._worker = None
        self._worker_thread = None
        self._sync_ui()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._worker:
            self._worker.stop()

        super().closeEvent(event)
