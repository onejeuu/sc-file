from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QPushButton, QSizePolicy, QWidget

from scfile.app.enums import TaskKind, TaskOutcome
from scfile.app.events import TaskError, TaskItem, TaskItemFailure, TaskStarted, TaskSummary
from scfile.app.gui import strings
from scfile.app.gui.styles import Colors, Styles

from .manager import TaskManager


OUTCOME_COLORS = {
    TaskOutcome.EMPTY: Colors.WARNING,
    TaskOutcome.COMPLETED: Colors.SUCCESS,
    TaskOutcome.PARTIAL: Colors.WARNING,
    TaskOutcome.FAILED: Colors.ERROR,
    TaskOutcome.CANCELLED: Colors.WARNING,
}

RESULT_KEYS = {
    (TaskKind.CONVERT, TaskOutcome.EMPTY): "task.result.convert.empty",
    (TaskKind.CONVERT, TaskOutcome.COMPLETED): "task.result.convert.simple",
}


def _result_key(summary: TaskSummary) -> str:
    if summary.outcome is TaskOutcome.CANCELLED:
        return f"task.cancelled.{summary.kind}"

    return RESULT_KEYS.get((summary.kind, summary.outcome), f"task.result.{summary.kind}")


class TaskWidget(QWidget):
    def __init__(self, tasks: TaskManager, parent: QWidget | None = None):
        super().__init__(parent)
        self.tasks = tasks
        self._completed = 0
        self._total = 0
        self._build_ui()

        tasks.busy_changed.connect(self._busy_changed)
        tasks.reported.connect(self._report)
        tasks.completed.connect(self._show_summary)
        self.hide()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(10)

        self.status = QLabel()
        self.status.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.progress = QProgressBar()
        self.progress.setMinimumWidth(220)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            f"QProgressBar {{ background: {Colors.CARD}; border: 1px solid {Colors.BORDER}; "
            f"border-radius: 3px; }} "
            f"QProgressBar::chunk {{ background: {Colors.ACCENT}; }}"
        )

        self.progress_text = QLabel()
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.cancel = QPushButton(strings.get("button.task.cancel"))
        self.cancel.setStyleSheet(Styles.BUTTON)
        self.cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel.clicked.connect(self._cancel)

        self.dismiss = QPushButton("×")
        self.dismiss.setFixedWidth(28)
        self.dismiss.setStyleSheet(Styles.BUTTON)
        self.dismiss.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dismiss.setToolTip(strings.get("tooltip.task.dismiss"))
        self.dismiss.clicked.connect(self.hide)
        self.dismiss.hide()

        layout.addWidget(self.status, 1)
        layout.addWidget(self.progress)
        layout.addWidget(self.progress_text)
        layout.addWidget(self.cancel)
        layout.addWidget(self.dismiss)

    def _busy_changed(self, busy: bool) -> None:
        if not busy:
            return

        self.status.setText(strings.get("task.running"))
        self.status.setStyleSheet(f"color: {Colors.TEXT};")
        self.progress.hide()
        self.progress_text.hide()
        self.cancel.setText(strings.get("button.task.cancel"))
        self.cancel.setEnabled(True)
        self.cancel.show()
        self.dismiss.hide()
        self.show()

    def _report(self, event: object) -> None:
        match event:
            case TaskStarted():
                self._show_running(event)
            case TaskItem() | TaskItemFailure():
                self._completed += 1
                self._show_progress()
            case TaskError():
                self._show_progress()

    def _show_running(self, event: TaskStarted) -> None:
        self._completed = 0
        self._total = event.total
        text = strings.get(f"task.running.{event.kind}").format(total=event.total)
        self._show_status(text, event.kind, event.output, Colors.TEXT)
        self._show_progress()

    def _show_progress(self) -> None:
        self.progress.setRange(0, self._total)
        self.progress.setValue(self._completed)
        percent = self._completed / self._total if self._total else 0.0
        self.progress_text.setText(f"{self._completed:,}/{self._total:,} · {percent:.0%}")
        self.progress.show()
        self.progress_text.show()

    def _show_summary(self, summary: object) -> None:
        if not isinstance(summary, TaskSummary):
            return

        self.progress.hide()
        self.progress_text.hide()
        self.cancel.hide()
        self.dismiss.show()

        values = {
            "completed": summary.work.completed,
            "total": summary.total or 0,
            "written": summary.files.written,
            "skipped": summary.files.skipped,
            "failed": summary.work.failed,
        }
        result = strings.get(_result_key(summary)).format(**values)
        details = tuple(
            strings.get(key).format(**values)
            for key, count in (
                ("task.errors", summary.work.failed),
                ("task.skipped", summary.files.skipped),
            )
            if count
        )
        text = " · ".join((result, *details))

        self._show_status(text, summary.kind, summary.output, OUTCOME_COLORS[summary.outcome])
        self.show()

    def _cancel(self) -> None:
        self.tasks.cancel()
        self.cancel.setText(strings.get("button.task.cancelling"))
        self.cancel.setEnabled(False)

    def _show_status(
        self,
        text: str,
        kind: TaskKind,
        output: Path | None,
        color: Colors,
    ) -> None:
        if output is None and kind is TaskKind.CONVERT:
            destination = strings.get("task.output.alongside")
        else:
            destination = str(output)

        message = f"{text} · {strings.get('task.output').format(output=destination)}"
        self.status.setText(message)
        self.status.setToolTip(message)
        self.status.setStyleSheet(f"color: {color};")
