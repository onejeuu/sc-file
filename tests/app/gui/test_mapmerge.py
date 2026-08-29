from pathlib import Path
from shutil import copyfile

from PySide6.QtWidgets import QApplication

from scfile.app.gui import strings
from scfile.app.gui.settings import Settings
from scfile.app.gui.tabs.mapmerge import MapMergeTab
from scfile.app.gui.tasks import TaskManager


SOURCE = Path(__file__).parents[2] / "assets/formats/textures/source/texture_rgba.ol"


def test_form(qapp: QApplication, tmp_path: Path) -> None:
    folder = tmp_path / "map"
    folder.mkdir()
    copyfile(SOURCE, folder / "r.0.0.ol")
    settings = Settings(export_path=tmp_path / "export")
    tab = MapMergeTab(TaskManager(), settings)

    tab.source.value = str(folder)

    assert Path(tab.output.value) == settings.export_path / "map.jpg"
    assert tab._submit_error() is None

    output = Path(tab.output.value)
    output.parent.mkdir()
    output.touch()
    tab._sync()
    assert strings.get("warning.mapmerge.overwrite") in tab.warnings.text()

    tab.output.value = str(tmp_path / "map.png")
    tab._edit_output(tab.output.value)
    assert tab._submit_error() == "tooltip.form.invalid"
    assert tab.output.invalid

    tab.deleteLater()
    qapp.processEvents()


def test_game_maps(qapp: QApplication, tmp_path: Path) -> None:
    game = tmp_path / "game"
    pda = game / "modassets/assets/pda"
    for name in ("map", "unknown", "sound", "textures"):
        folder = pda / name
        folder.mkdir(parents=True)
        copyfile(SOURCE, folder / "r.0.0.ol")

    tab = MapMergeTab(TaskManager(), Settings(game_root=game, export_path=tmp_path / "export"))

    assert Path(tab.source.value) == game
    assert tab.map.isEnabled()
    assert {tab.map.itemData(index).name for index in range(tab.map.count())} == {"map", "unknown"}
    assert strings.mapmerge_map("unknown") == "unknown"
    assert Path(tab.output.value) == tmp_path / "export/map.jpg"
    assert tab._submit_error() is None

    tab.map.setCurrentIndex(1)
    assert Path(tab.output.value) == tmp_path / "export/unknown.jpg"

    tab.source.value = str(pda / "map")
    assert tab.map.currentData() == pda / "map"

    tab.deleteLater()
    qapp.processEvents()


def test_game_maps_without_path_resolution(qapp: QApplication, tmp_path: Path) -> None:
    game = tmp_path / "game"
    folder = game / "modassets/assets/pda/map"
    folder.mkdir(parents=True)
    copyfile(SOURCE, folder / "r.0.0.ol")

    tab = MapMergeTab(TaskManager(), Settings(resolve_paths=False))
    tab.source.value = str(game)

    assert not tab.map.isEnabled()
    assert not tab.map.count()
    assert tab.map.placeholderText() == strings.get("placeholder.mapmerge.map")
    assert tab.map_cursor.overlay.toolTip() == strings.get("tooltip.mapmerge.map")

    tab.deleteLater()
    qapp.processEvents()
