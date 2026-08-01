"""Qt adapter for application tasks."""

from time import monotonic

from PySide6.QtCore import QObject, QThread, Signal, Slot

from scfile.app.tasks import Context, Item, Progress, Summary, Task
from scfile.app.tasks.base import failure


class TaskWorker(QObject):
    """Run an application task in a Qt thread."""

    reported = Signal(object)
    completed = Signal(object)
    finished = Signal()

    def __init__(self, task: Task):
        super().__init__()
        self.task = task
        self.context = Context(report=self._report)
        self._progress: Progress | None = None
        self._emitted: Progress | None = None
        self._reported_at = 0.0

    def _report(self, event: object) -> None:
        # Successful items are reflected by progress and the final summary.
        if isinstance(event, Item):
            return

        if not isinstance(event, Progress):
            self.reported.emit(event)
            return

        self._progress = event
        now = monotonic()
        final = event.total is not None and event.completed >= event.total
        if event.completed == 0 or final or now - self._reported_at >= 0.1:
            self.reported.emit(event)
            self._emitted = event
            self._reported_at = now

    def _flush_progress(self) -> None:
        if self._progress is not None and self._progress != self._emitted:
            self.reported.emit(self._progress)
            self._emitted = self._progress

    @Slot()
    def run(self) -> None:
        try:
            summary = self.task.run(self.context)
        except Exception as error:
            self.reported.emit(failure(type(self.task).__name__, error, unexpected=True))
            summary = Summary(
                name=type(self.task).__name__,
                total=0,
                completed=0,
                failed=1,
                cancelled=self.context.stopped,
            )
        self._flush_progress()
        self.completed.emit(summary)
        self.finished.emit()

    def stop(self) -> None:
        self.context.stop()


class TaskManager(QObject):
    """Own the single active heavy GUI task."""

    reported = Signal(object)
    completed = Signal(object)
    busy_changed = Signal(bool)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._worker: TaskWorker | None = None
        self._thread: QThread | None = None

    @property
    def busy(self) -> bool:
        return self._thread is not None

    def start(
        self,
        task: Task,
    ) -> bool:
        """Start a task unless another heavy task is active."""

        if self.busy:
            return False

        thread = QThread(self)
        worker = TaskWorker(task)
        worker.moveToThread(thread)

        worker.reported.connect(self.reported.emit)
        worker.completed.connect(self.completed.emit)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._release)
        thread.finished.connect(thread.deleteLater)
        thread.started.connect(worker.run)

        self._worker = worker
        self._thread = thread
        self.busy_changed.emit(True)
        thread.start()
        return True

    @Slot()
    def _release(self) -> None:
        self._worker = None
        self._thread = None
        self.busy_changed.emit(False)

    def cancel(self) -> None:
        """Request cancellation of the active task."""

        worker = self._worker
        if worker is None:
            return

        worker.stop()
