from __future__ import annotations

import os
from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def qapp(tmp_path_factory: pytest.TempPathFactory) -> Iterator[QApplication]:
    from PySide6.QtCore import QSettings
    from PySide6.QtWidgets import QApplication

    settings = tmp_path_factory.mktemp("settings")
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(settings))

    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication([])
    yield app
    app.processEvents()
