from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from scfile.app.events import TaskItem, TaskItemFailure, TaskStarted, TaskSummary
from scfile.app.gui import strings
from scfile.app.gui.settings import Settings
from scfile.app.gui.styles import Styles
from scfile.app.gui.tasks import TaskManager
from scfile.app.gui.widgets.disabled import DisabledCursor
from scfile.app.gui.widgets.path import PathField
from scfile.app.gui.widgets.progress import ProgressButton
from scfile.app.gui.widgets.warnings import WarningsWidget
from scfile.app.tasks.mapmerge import MapMergeTask
from scfile.convert import mapmerge
from scfile.options import Options


class MapMergeTab(QWidget):
    def __init__(self, tasks: TaskManager, settings: Settings):
        super().__init__()
        self.tasks = tasks
        self.settings = settings
        self.source_touched = False
        self.output_touched = False
        self.running = False
        self._build_ui()

        self.tasks.busy_changed.connect(self._sync)
        self.tasks.reported.connect(self._report)
        self.tasks.completed.connect(self._complete)
        self._sync()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        self.source = PathField(
            f"{strings.get('label.mapmerge.source')} (.ol)",
            placeholder="pda/map",
            caption=strings.get("dialog.mapmerge.source"),
        )
        self.source.changed.connect(self._edit_source)
        self.source.text_changed.connect(self._source_changed)

        self.output = PathField(
            f"{strings.get('label.mapmerge.output')} (.jpg)",
            placeholder=strings.get("placeholder.path"),
            caption=strings.get("dialog.mapmerge.output"),
            mode="save",
            file_filter="JPEG (*.jpg)",
            default_suffix=".jpg",
        )
        self.output.changed.connect(self._edit_output)

        layout.addWidget(self.source)
        layout.addWidget(self.output)

        self.warnings = WarningsWidget()
        layout.addWidget(self.warnings)
        layout.addStretch()

        self.submit = ProgressButton(strings.get("button.mapmerge"))
        self.submit.setFixedHeight(50)
        self.submit.setStyleSheet(Styles.BUTTON_ACCENT)
        self.submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit.clicked.connect(self._start_merge)
        layout.addWidget(self.submit)
        self.submit_cursor = DisabledCursor(self.submit)

    def apply_export_path(self, path: Path) -> None:
        self.settings.export_path = path
        self._source_changed(self.source.value)

    def apply_path_resolution(self) -> None:
        self._source_changed(self.source.value)

    def _suggested_output(self) -> Path | None:
        source = Path(self.source.value.strip())
        if not self.settings.resolve_paths or not source.is_dir():
            return None
        return self.settings.export_path / f"{source.name}.jpg"

    def _source_changed(self, _: str) -> None:
        value = self.source.value.strip()
        if value and self.settings.resolve_paths:
            source = Path(value)
            if source.is_dir() and source.resolve() != source:
                self.source.value = source.resolve().as_posix()
                return

        suggested = self._suggested_output()
        if suggested is not None:
            self.output.value = suggested.as_posix()
        elif self.settings.resolve_paths:
            self.output.value = ""
        self._sync()

    def _edit_source(self, value: str) -> None:
        self.source_touched = True
        self._source_changed(value)

    def _edit_output(self, _: str) -> None:
        self.output_touched = True
        self._sync()

    def _source_invalid(self) -> bool:
        value = self.source.value.strip()
        if not value:
            return True

        source = Path(value)
        if not source.is_dir():
            return True

        try:
            return not mapmerge.scan(source)

        except OSError:
            return True

    def _output_invalid(self) -> bool:
        value = self.output.value.strip()
        output = Path(value)
        return not value or output.is_dir() or output.suffix.lower() != ".jpg"

    def _submit_error(self) -> str | None:
        errors = (
            "tooltip.task.busy" if self.tasks.busy and not self.running else None,
            "tooltip.form.invalid" if self._source_invalid() or self._output_invalid() else None,
        )
        return next((error for error in errors if error), None)

    def _sync(self) -> None:
        suggested = self._suggested_output()
        self.output.initial_path = (suggested or self.settings.export_path).as_posix()

        source_invalid = self.source_touched and self._source_invalid()
        source_error = strings.get("tooltip.mapmerge.invalid.source") if source_invalid else None
        self.source.set_error(source_error)

        output_invalid = self.output_touched and self._output_invalid()
        output_error = strings.get("tooltip.mapmerge.invalid.output") if output_invalid else None
        self.output.set_error(output_error)

        output = Path(self.output.value.strip())
        warnings = (strings.get("warning.mapmerge.overwrite"),) if output.is_file() else ()
        self.warnings.set_messages(warnings)

        error = self._submit_error()
        self.submit_cursor.set(self.running or error is None, strings.get(error or ""))

    def _start_merge(self) -> None:
        if self.running:
            self.tasks.cancel()
            return

        task = MapMergeTask(
            Path(self.source.value.strip()),
            Path(self.output.value.strip()),
            Options(),
        )
        self.running = self.tasks.start(task)
        if self.running:
            self.submit.start()
            self.submit_cursor.set(True)
        self._sync()

    def _report(self, event: object) -> None:
        if not self.running:
            return

        match event:
            case TaskStarted():
                self.submit.start(event.total)
                self.submit_cursor.set(True)
            case TaskItem() | TaskItemFailure():
                self.submit.advance()

    def _complete(self, summary: object) -> None:
        if self.running and isinstance(summary, TaskSummary):
            self.running = False
            self.submit.finish()
            self._sync()
