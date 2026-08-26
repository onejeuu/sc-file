from pathlib import Path

from PySide6.QtCore import QSettings

from scfile.app.gui.settings import Settings, Store


def test_store(tmp_path: Path) -> None:
    data = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    store = Store(data)
    expected = Settings(
        game_root=tmp_path / "game",
        resolve_paths=False,
        verbose=True,
        export_path=tmp_path / "export",
    )
    store.save(expected)

    assert store.load() == expected


def test_store_defaults(tmp_path: Path) -> None:
    data = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)

    assert Store(data).load() == Settings()
