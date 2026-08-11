from pathlib import Path

from PySide6.QtWidgets import QApplication

from scfile.app.enums import OutputLayout
from scfile.app.formats import model_formats
from scfile.app.gui.settings import Settings
from scfile.app.gui.tabs.animate import ArmsForm, BodyForm
from scfile.app.gui.tabs.convert import ConvertForm, ConvertTab
from scfile.app.gui.tasks import TaskManager


def test_convert_form(qapp: QApplication) -> None:
    form = ConvertForm()

    assert form.filters
    assert form.output is not None
    assert form.output_valid
    assert form.output_layout is OutputLayout.ROOTED
    assert tuple(form.model_format.itemData(index) for index in range(form.model_format.count())) == model_formats()

    form.output_path.value = ""
    assert form.output is None
    assert not form.output_valid

    form.output_origin.setChecked(True)
    assert form.output is None
    assert form.output_valid

    form.output_path.activated.emit()
    assert form.output_custom.isChecked()
    assert not form.output_path.read_only

    form.deleteLater()
    qapp.processEvents()


def test_convert_remembers_output(qapp: QApplication, tmp_path: Path) -> None:
    settings = Settings(remember_output=True)
    tab = ConvertTab(TaskManager(), settings)
    output = tmp_path / "export"
    tab.form.output_path.value = str(output)
    tab.form.output_changed.emit(tab.form.output)

    assert settings.output == output

    tab.deleteLater()
    qapp.processEvents()


def test_body_form(qapp: QApplication, tmp_path: Path) -> None:
    animation = tmp_path / "library.mcal"
    model = tmp_path / "model.mcsb"
    animation.touch()
    model.touch()

    form = BodyForm()
    form.source.value = str(animation)
    form.model.value = str(model)

    assert form.validation_error() is None
    task = form.create_task(tmp_path / "output.glb")
    assert task.source == animation
    assert task.models == (model,)

    form.deleteLater()
    qapp.processEvents()


def test_arms_form(qapp: QApplication, tmp_path: Path) -> None:
    animation = tmp_path / "wpn_fp_test.mcvd"
    model = tmp_path / "model.mcsb"
    hands = tmp_path / "hands.mcsb"
    for path in (animation, model, hands):
        path.touch()

    form = ArmsForm()
    form.source.value = str(animation)
    form.model.value = str(model)
    form.hands.value = str(hands)

    assert form.validation_error() is None
    assert form.create_task(tmp_path / "output.glb").models == (model, hands)

    form.hands.value = str(tmp_path / "invalid.obj")
    assert form.validation_error() == "tooltip.animate.invalid.additional"

    form.deleteLater()
    qapp.processEvents()
