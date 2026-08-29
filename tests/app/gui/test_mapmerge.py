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
