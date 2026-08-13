from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from scfile.app.enums import OutputLayout
from scfile.app.formats import model_formats
from scfile.app.gui.settings import Settings
from scfile.app.gui.tabs.convert import ConvertForm, ConvertTab
from scfile.app.gui.tasks import TaskManager
from scfile.core import ModelEncoder
from scfile.formats import registry


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
@pytest.mark.parametrize("fmt", model_formats())
def test_convert_features(qapp: QApplication, fmt) -> None:
    form = ConvertForm()
    form.model_format.setCurrentIndex(form.model_format.findData(fmt))

    for feature, checkbox in form.features.items():
        encoder = registry.encoders[fmt]
        assert issubclass(encoder, ModelEncoder)
        assert checkbox.isEnabled() is encoder.supports(feature)

    form.deleteLater()
    qapp.processEvents()


def test_default_output(qapp: QApplication, tmp_path: Path) -> None:
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


def test_empty_output(qapp: QApplication, tmp_path: Path) -> None:
    tab = ConvertTab(TaskManager(), Settings())
    tab.form.output_path.value = ""
    tab.form.output_changed.emit(None)
    source = tmp_path / "modassets/assets"

    assert not tab._warnings((source,), None)

    tab.deleteLater()
    qapp.processEvents()
