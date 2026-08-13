from pathlib import Path

from PySide6.QtCore import QSettings

from scfile.app.gui.settings import Settings, Store


def test_store(tmp_path: Path) -> None:
    data = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    store = Store(data)
    default = tmp_path / "default"
    store.save(Settings(export_path=default))

    settings = store.load()
    assert settings.export_path == default
