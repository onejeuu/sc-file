from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from scfile.cli.cmd.convert import convert_command
from tests.conftest import ASSETS


runner = CliRunner()

MODEL = "model_v12.mcsb"
TEXTURE = "texture_dxt1.ol"
IMAGE = "image.mic"


def test_default():
    src = ASSETS / "cli" / MODEL
    with patch("scfile.cli.cmd.convert.convert.auto") as convert_auto:
        result = runner.invoke(convert_command, [str(src)])
        assert result.exit_code == 0
        convert_auto.assert_called_once()


def test_relative_no_output():
    src = ASSETS / "cli" / MODEL
    with patch("scfile.cli.cmd.convert.convert.auto"):
        result = runner.invoke(convert_command, [str(src), "--relative"])
        assert result.exit_code == 0
        assert result.output


def test_convert_single_file(temp: Path):
    src = ASSETS / "cli" / MODEL
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0
    assert (temp / "model_v12.obj").exists()


def test_convert_mdlformat(temp: Path):
    src = ASSETS / "cli" / MODEL
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "-F", "obj"])
    assert result.exit_code == 0
    assert (temp / "model_v12.obj").exists()
    assert not (temp / "model_v12.glb").exists()


def test_convert_skeleton(temp: Path):
    src = ASSETS / "cli" / MODEL
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--skeleton"])
    assert result.exit_code == 0


def test_convert_animation(temp: Path):
    src = ASSETS / "cli" / MODEL
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--animation"])
    assert result.exit_code == 0


def test_convert_on_conflict_rename(temp: Path):
    src = ASSETS / "cli" / MODEL
    (temp / "model_v12.obj").write_text("existing")
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--on-conflict", "rename"])
    assert result.exit_code == 0
    assert (temp / "model_v12 (1).obj").exists()


def test_convert_on_conflict_skip(temp: Path):
    src = ASSETS / "cli" / MODEL
    (temp / "model_v12.obj").write_text("existing")
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--on-conflict", "skip"])
    assert result.exit_code == 0
    assert (temp / "model_v12.obj").read_text() == "existing"


def test_convert_missing_file(temp: Path):
    result = runner.invoke(convert_command, [str(temp / "missing.mcsb")])
    assert result.exit_code != 0


def test_convert_texture(temp: Path):
    src = ASSETS / "cli" / TEXTURE
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0
    assert list(temp.glob("*.dds"))


def test_convert_image(temp: Path):
    src = ASSETS / "cli" / IMAGE
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0
    assert list(temp.glob("*.png"))


def test_relative(temp: Path):
    src = ASSETS / "cli"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--relative"])
    assert result.exit_code == 0
    assert (temp / "sub" / "sub_model_v12.obj").exists()


def test_parent(temp: Path):
    src = ASSETS / "cli"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--parent"])
    assert result.exit_code == 0
    assert (temp / "cli" / "sub" / "sub_model_v12.obj").exists()


def test_relative_flat_output(temp: Path):
    src = ASSETS / "cli"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0
    assert (temp / "model_v12.obj").exists()
    assert (temp / "sub_model_v12.obj").exists()
    assert not (temp / "sub").exists()


def test_relative_with_parent(temp: Path):
    src = ASSETS / "cli" / "sub"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--parent"])
    assert result.exit_code == 0
    assert (temp / "sub" / "sub_model_v12.obj").exists()


def test_parent_implies_relative(temp: Path):
    src = ASSETS / "cli" / "sub"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--parent"])
    assert result.exit_code == 0
    assert (temp / "sub" / "sub_model_v12.obj").exists()


def test_multiple_sources(temp: Path):
    src1 = ASSETS / "cli" / MODEL
    src2 = ASSETS / "cli" / TEXTURE
    result = runner.invoke(convert_command, [str(src1), str(src2), "-O", str(temp)])
    assert result.exit_code == 0
    assert (temp / "model_v12.obj").exists()
    assert list(temp.glob("*.dds"))


def test_overwrite_default(temp: Path):
    src = ASSETS / "cli" / MODEL
    (temp / "model_v12.obj").write_text("old")
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0
    assert (temp / "model_v12.obj").read_text() != "old"


def test_skeleton_obj_warns(temp: Path):
    src = ASSETS / "cli" / MODEL
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "-F", "obj", "--skeleton"])
    assert result.exit_code == 0


def test_animation_obj_warns(temp: Path):
    src = ASSETS / "cli" / MODEL
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "-F", "obj", "--animation"])
    assert result.exit_code == 0


def test_invalid_structure_error(temp: Path):
    src = ASSETS / "invalid" / "broken.ol"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0


def test_empty_file_error(temp: Path):
    src = ASSETS / "invalid" / "empty.mic"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0


def test_unexpected_error(temp: Path):
    src = ASSETS / "cli" / MODEL
    with patch("scfile.cli.cmd.convert.convert.auto", side_effect=RuntimeError("boom")):
        result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
        assert result.exit_code == 0
