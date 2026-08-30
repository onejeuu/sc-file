from pathlib import Path
from shutil import copyfile

from PySide6.QtWidgets import QApplication

from scfile.app.gui.settings import Settings
from scfile.app.gui.tabs.maptiles import MapTilesTab
from scfile.app.gui.tasks import TaskManager
from scfile.app.tasks.maptiles import MapTilesImage


SOURCE = Path(__file__).parents[2] / "assets/formats/textures/source/texture_rgba.ol"


def test_flat(qapp: QApplication, tmp_path: Path) -> None:
    folder = tmp_path / "map"
    folder.mkdir()
    copyfile(SOURCE, folder / "r.0.0.ol")
    settings = Settings(export_path=tmp_path / "export")
    tab = MapTilesTab(TaskManager(), settings)

    tab.source.value = str(folder)

    assert not tab.region.isEnabled()
    assert not tab.map.isEnabled()
    assert len(tab.tiles) == 1
    assert Path(tab.output.value) == settings.export_path / "map.jpg"
    assert tab.encoding.format is MapTilesImage.JPEG
    assert not tab.estimate.isHidden()
    assert tab._submit_error() is None

    tab.source.value = str(tmp_path / "missing")
    assert not tab.tiles
    assert not tab.output.value

    tab.source.value = str(folder)
    output = Path(tab.output.value)
    output.parent.mkdir()
    output.touch()
    tab._sync()
    assert not tab.warnings.isHidden()

    tab.output.value = str(tmp_path / "map.png")
    tab._edit_output(tab.output.value)
    assert tab.encoding.format is MapTilesImage.PNG
    assert tab._submit_error() is None
    assert not tab.output.invalid

    tab.deleteLater()
    qapp.processEvents()


def test_encoding(qapp: QApplication, tmp_path: Path) -> None:
    folder = tmp_path / "map"
    folder.mkdir()
    copyfile(SOURCE, folder / "r.0.0.ol")
    tab = MapTilesTab(TaskManager(), Settings(export_path=tmp_path))
    tab.source.value = str(folder)

    tab.encoding.spin.setValue(95)
    tab.encoding._buttons[MapTilesImage.PNG].click()
    assert tab.encoding.format is MapTilesImage.PNG
    assert Path(tab.output.value) == tmp_path / "map.png"

    tab.encoding.slider.setValue(8)
    assert tab.encoding.spin.value() == 8
    assert tab.encoding.save == {"format": "PNG", "compress_level": 8}
    tab.encoding._buttons[MapTilesImage.JPEG].click()
    assert Path(tab.output.value) == tmp_path / "map.jpg"
    assert tab.encoding.spin.value() == 95
    assert tab.encoding.save == {"format": "JPEG", "quality": 95}

    tab.output.value = str(tmp_path / "manual.jpeg")
    tab._edit_output(tab.output.value)
    assert tab.encoding.format is MapTilesImage.JPEG
    assert Path(tab.output.value) == tmp_path / "manual.jpeg"

    tab.output.value = str(tmp_path / "manual.unknown")
    tab._edit_output(tab.output.value)
    assert tab.encoding.format is MapTilesImage.JPEG
    assert tab._output_invalid()

    tab.deleteLater()
    qapp.processEvents()


def test_game(qapp: QApplication, tmp_path: Path) -> None:
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

    tab = MapTilesTab(TaskManager(), Settings(game_root=game, export_path=tmp_path / "export"))

    assert Path(tab.source.value) == pda
    assert tab.region.isEnabled()
    assert tab.region.currentData() == "ru"
    assert tab.map.isEnabled()
    assert {tab.map.itemData(index) for index in range(tab.map.count())} == {"map", "map_bar_save", "unknown"}
    assert Path(tab.output.value) == tmp_path / "export/map.jpg"
    assert tab._submit_error() is None
    assert tab._sources() == (pda / "map", patch)

    tab.encoding._buttons[MapTilesImage.PNG].click()
    assert Path(tab.output.value) == tmp_path / "export/map.png"

    index = tab.map.findData("unknown")
    tab.map.setCurrentIndex(index)
    tab.map.activated.emit(index)
    assert Path(tab.output.value) == tmp_path / "export/unknown.png"

    tab.source.value = str(pda / "map_overlay")
    assert not tab._sources()

    tab.source.value = str(pda / "map")
    assert not tab.map.isEnabled()
    assert tab.map.currentData() == "map"
    assert tab.region.isEnabled()
    assert Path(tab.output.value) == tmp_path / "export/map.png"

    tab.deleteLater()
    qapp.processEvents()


def test_region(qapp: QApplication, tmp_path: Path) -> None:
    game = tmp_path / "game"
    base = game / "modassets/assets/pda/map"
    ru = game / "modassets/assets/_localized/ru/pda/map_ru"
    en = game / "modassets/assets/_localized/en/pda/map_en"
    global_patch = game / "bin_global/patchassets/assets/pda/map"
    for folder in (base, ru, en, global_patch):
        folder.mkdir(parents=True)
        copyfile(SOURCE, folder / "r.0.0.ol")

    tab = MapTilesTab(TaskManager(), Settings(game_root=game))

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


def test_manual_paths(qapp: QApplication, tmp_path: Path) -> None:
    game = tmp_path / "game"
    folder = game / "modassets/assets/pda/map"
    folder.mkdir(parents=True)
    copyfile(SOURCE, folder / "r.0.0.ol")

    tab = MapTilesTab(TaskManager(), Settings(resolve_paths=False))
    tab.source.value = str(game)

    assert not tab.map.isEnabled()
    assert tab.map.currentData() is None

    tab.source.value = str(game / "modassets/assets/pda")
    assert tab.map.isEnabled()
    assert tab.map.currentData() == "map"
    assert not tab.output.value

    tab.source.value = str(folder)
    assert Path(tab.source.value) == folder
    assert not tab.map.isEnabled()
    assert tab.map.currentData() == "map"

    tab.deleteLater()
    qapp.processEvents()
