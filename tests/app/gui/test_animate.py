from pathlib import Path

from PySide6.QtWidgets import QApplication

from scfile.app.gui.settings import Settings
from scfile.app.gui.tabs.animate import AnimateTab, ArmsForm, BodyForm
from scfile.app.gui.tasks import TaskManager


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

    form.model.value = ""
    assert form.validation_error() is None
    assert form.create_task(tmp_path / "output.glb").models == (None, hands)

    form.model.value = str(model)
    form.hands.value = ""
    assert form.validation_error() is None
    assert form.create_task(tmp_path / "output.glb").models == (model, None)

    form.model.value = ""
    assert form.validation_error() == "tooltip.animate.invalid.arms"

    form.hands.value = str(tmp_path / "invalid.obj")
    form._touch_input(form.hands)
    assert form.validation_error() is not None
    assert form.hands.invalid
    assert not form.hands.error.isHidden()

    form.deleteLater()
    qapp.processEvents()


def test_export(qapp: QApplication, tmp_path: Path) -> None:
    settings = Settings(export_path=tmp_path / "export")
    tab = AnimateTab(TaskManager(), settings)
    arms = tmp_path / "arms.mcvd"
    body = tmp_path / "body.mcal"
    arms.touch()
    body.touch()

    tab.form.source.value = str(arms)
    tab._sync()
    assert Path(tab.output.value) == settings.export_path / "arms.glb"

    tab.tabs.setCurrentIndex(1)
    assert not tab.output.value

    tab.form.source.value = str(body)
    tab._sync()
    assert Path(tab.output.value) == settings.export_path / "body.glb"

    tab.tabs.setCurrentIndex(0)
    assert Path(tab.output.value) == settings.export_path / "arms.glb"

    custom = tmp_path / "custom.glb"
    tab.output.value = str(custom)
    tab._output_changed(str(custom))
    tab.apply_export_path(tmp_path / "other")
    assert Path(tab.output.value) == custom

    tab.deleteLater()
    qapp.processEvents()


def test_output(qapp: QApplication, tmp_path: Path) -> None:
    settings = Settings(export_path=tmp_path / "export")
    tab = AnimateTab(TaskManager(), settings)
    first = tmp_path / "first.mcvd"
    second = tmp_path / "second.mcvd"
    invalid = tmp_path / "invalid.obj"
    for path in (first, second, invalid):
        path.touch()

    tab.form.source.value = str(first)
    tab._sync()
    assert Path(tab.output.value) == settings.export_path / "first.glb"

    tab.form.source.value = str(second)
    tab._sync()
    assert Path(tab.output.value) == settings.export_path / "second.glb"

    tab.output.value = str(tmp_path / "manual.glb")
    tab._output_changed(tab.output.value)
    tab.form.source.value = str(first)
    tab._sync()
    assert Path(tab.output.value) == tmp_path / "manual.glb"

    tab.output.value = ""
    tab._output_changed("")
    assert Path(tab.output.value) == settings.export_path / "first.glb"

    tab.form.source.value = str(invalid)
    tab._sync()
    assert not tab.output.value

    tab.deleteLater()
    qapp.processEvents()


def test_paths(qapp: QApplication, tmp_path: Path) -> None:
    settings = Settings(export_path=tmp_path / "export", resolve_paths=False)
    tab = AnimateTab(TaskManager(), settings)
    source = tmp_path / "animation.mcvd"
    source.touch()

    tab.form.source.value = str(source)
    tab._sync()
    assert not tab.output.value

    settings.resolve_paths = True
    tab.apply_path_resolution()
    assert Path(tab.output.value) == settings.export_path / "animation.glb"

    tab.deleteLater()
    qapp.processEvents()


def test_invalid(qapp: QApplication, tmp_path: Path) -> None:
    form = ArmsForm()
    form.source.value = str(tmp_path / "animation.obj")
    form._touch_input(form.source)
    form.validation_error()

    assert form.source.invalid
    assert not form.source.error.isHidden()

    form.deleteLater()
    qapp.processEvents()
