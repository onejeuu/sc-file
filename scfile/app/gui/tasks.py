from PySide6.QtCore import QObject, QThread, Signal, Slot

from scfile.app.gui import threads
from scfile.app.tasks import Task, TaskContext, execute


class TaskWorker(threads.JobWorker):
    reported = Signal(object)
    completed = Signal(object)

    def __init__(self, task: Task, context: TaskContext):
        super().__init__()
        self.task = task
        self.context = context

    def _run(self) -> None:
        summary = execute(self.task, self.reported.emit, self.context)
        self.completed.emit(summary)


class TaskManager(QObject):
    reported = Signal(object)
    completed = Signal(object)
    busy_changed = Signal(bool)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._context: TaskContext | None = None
        self._worker: TaskWorker | None = None
        self._thread: QThread | None = None

    @property
    def busy(self) -> bool:
        return self._thread is not None

    def start(self, task: Task) -> bool:
        if self.busy:
            return False

        context = TaskContext()
        worker = TaskWorker(task, context)

        worker.reported.connect(self.reported.emit)
        worker.completed.connect(self.completed.emit)
        self._context = context
        self._worker = worker
        self._thread = threads.job(self, worker)
        self._thread.finished.connect(self._clear_active_task)
        self.busy_changed.emit(True)
        self._thread.start()
        return True

    def cancel(self) -> None:
        if self._context is not None:
            self._context.stop()

    @Slot()
    def _clear_active_task(self) -> None:
        self._context = None
        self._worker = None
        self._thread = None
        self.busy_changed.emit(False)
