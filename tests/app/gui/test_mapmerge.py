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

    assert not tab.region.isEnabled()
    assert not tab.region.count()
    assert not tab.map.isEnabled()
    assert not tab.map.count()
    assert tab.map.placeholderText() == strings.get("placeholder.mapmerge.map")
    assert tab.map_cursor.overlay.toolTip() == strings.get("tooltip.mapmerge.map")
    assert Path(tab.output.value) == settings.export_path / "map.jpg"
    assert tab._submit_error() is None

    output = Path(tab.output.value)
    output.parent.mkdir()
    output.touch()
    tab._sync()
    assert strings.get("warning.mapmerge.overwrite") in tab.warnings.text()

    tab.output.value = str(tmp_path / "map.png")
    tab._edit_output(tab.output.value)
    assert tab._submit_error() is None
    assert not tab.output.invalid

    tab.deleteLater()
    qapp.processEvents()


def test_game_maps(qapp: QApplication, tmp_path: Path) -> None:
    game = tmp_path / "game"
    pda = game / "modassets/assets/pda"
    for name in ("map", "unknown", "sound", "textures", "map_overlay"):
        folder = pda / name
        folder.mkdir(parents=True)
        copyfile(SOURCE, folder / "r.0.0.ol")

    localized = game / "modassets/assets/_localized/ru/pda/map_bar_save"
    localized.mkdir(parents=True)
    copyfile(SOURCE, localized / "r.0.0.ol")

    patch = game / "bin_ru/patchassets/assets/pda/map"
    patch.mkdir(parents=True)
    copyfile(SOURCE, patch / "r.1.0.ol")

    tab = MapMergeTab(TaskManager(), Settings(game_root=game, export_path=tmp_path / "export"))

    assert Path(tab.source.value) == pda
    assert tab.region.isEnabled()
    assert tab.region.currentData() == "ru"
    assert tab.map.isEnabled()
    assert {tab.map.itemData(index) for index in range(tab.map.count())} == {"map", "map_bar_save", "unknown"}
    assert strings.get("mapmerge.map.unknown", "unknown") == "unknown"
    assert Path(tab.output.value) == tmp_path / "export/map.jpg"
    assert tab._submit_error() is None
    assert tab._sources() == (pda / "map", patch)

    index = tab.map.findData("unknown")
    tab.map.setCurrentIndex(index)
    tab.map.activated.emit(index)
    assert Path(tab.output.value) == tmp_path / "export/unknown.jpg"

    tab.source.value = str(pda / "map_overlay")
    assert not tab._sources()

    tab.source.value = str(pda / "map")
    assert not tab.map.isEnabled()
    assert tab.map.count() == 3
    assert tab.map.currentData() == "map"
    assert tab.region.isEnabled()
    assert tab.map_cursor.overlay.toolTip() == strings.get("tooltip.mapmerge.fixed.map")
    assert Path(tab.output.value) == tmp_path / "export/map.jpg"

    tab.deleteLater()
    qapp.processEvents()


def test_game_region(qapp: QApplication, tmp_path: Path) -> None:
    game = tmp_path / "game"
    base = game / "modassets/assets/pda/map"
    ru = game / "modassets/assets/_localized/ru/pda/map_ru"
    en = game / "modassets/assets/_localized/en/pda/map_en"
    global_patch = game / "bin_global/patchassets/assets/pda/map"
    for folder in (base, ru, en, global_patch):
        folder.mkdir(parents=True)
        copyfile(SOURCE, folder / "r.0.0.ol")

    tab = MapMergeTab(TaskManager(), Settings(game_root=game))

    index = tab.region.findData("ru")
    tab.region.setCurrentIndex(index)
    tab.region.activated.emit(index)
    assert {tab.map.itemData(index) for index in range(tab.map.count())} == {"map", "map_ru"}

    index = tab.region.findData("en")
    tab.region.setCurrentIndex(index)
    tab.region.activated.emit(index)
    assert {tab.map.itemData(index) for index in range(tab.map.count())} == {"map", "map_en"}
    assert tab._sources() == (base, global_patch)

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

    tab.source.value = str(game / "modassets/assets/pda")
    assert tab.map.isEnabled()
    assert tab.map.count() == 1
    assert tab.map.currentData() == "map"
    assert not tab.output.value

    tab.source.value = str(folder)
    assert Path(tab.source.value) == folder
    assert not tab.map.isEnabled()
    assert tab.map.count() == 1
    assert tab.map.currentData() == "map"
    assert tab.map_cursor.overlay.toolTip() == strings.get("tooltip.mapmerge.fixed.map")

    tab.deleteLater()
    qapp.processEvents()
