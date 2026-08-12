from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from scfile.app.enums import OutputLayout
from scfile.app.formats import FORMAT_GROUPS, model_formats
from scfile.app.gui.settings import Settings
from scfile.app.gui.tabs.animate import AnimateTab, ArmsForm, BodyForm
from scfile.app.gui.tabs.convert import ConvertForm, ConvertTab
from scfile.app.gui.tasks import TaskManager
from scfile.registry import REGISTRY


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


def test_convert_groups_use_registry_filters() -> None:
    models = next(group for group in FORMAT_GROUPS if group.name == "models")
    nbt = next(group for group in FORMAT_GROUPS if group.name == "nbt")

    assert ".mcsa" in models.filters
    assert ".mcsa" not in models.display
    assert "itemnames.dat" in nbt.filters
    assert nbt.display == ("itemnames.dat", "prefs", "sd1…sd4")


@pytest.mark.parametrize("fmt", model_formats())
def test_convert_disables_unsupported_features(qapp: QApplication, fmt) -> None:
    form = ConvertForm()
    form.model_format.setCurrentIndex(form.model_format.findData(fmt))

    for feature, checkbox in form.features.items():
        assert checkbox.isEnabled() is REGISTRY.model_supports(fmt, feature)

    form.deleteLater()
    qapp.processEvents()


def test_convert_keeps_default_output(qapp: QApplication, tmp_path: Path) -> None:
    default = tmp_path / "default"
    settings = Settings(export_path=default)
    tab = ConvertTab(TaskManager(), settings)
    temporary = tmp_path / "temporary"
    tab.form.output_path.value = str(temporary)
    tab.form.output_changed.emit(tab.form.output)

    assert settings.export_path == default

    tab.apply_export_path(tmp_path / "changed")
    tab.form.output_path.value = ""
    tab.form.output_path.clear_requested.emit()
    assert tab.form.output == tmp_path / "changed"

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


def test_animate_uses_default_export(qapp: QApplication, tmp_path: Path) -> None:
    settings = Settings(export_path=tmp_path / "export")
    tab = AnimateTab(TaskManager(), settings)
    source = tmp_path / "run.mcvd"
    source.touch()

    tab.form.source.value = str(source)
    tab._sync()
    assert Path(tab.output.value) == settings.export_path / "run.glb"

    custom = tmp_path / "custom.glb"
    tab.output.value = str(custom)
    tab._output_changed(str(custom))
    tab.apply_export_path(tmp_path / "other")
    assert Path(tab.output.value) == custom

    tab.deleteLater()
    qapp.processEvents()
