from pathlib import Path

from PySide6.QtCore import QSettings

from scfile.app.gui.settings import Settings, Store


def test_store_remembers_output(tmp_path: Path) -> None:
    data = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    store = Store(data)
    output = tmp_path / "export"

    store.save(Settings(remember_output=True, output=output))

    settings = store.load()
    assert settings.remember_output
    assert settings.output == output
