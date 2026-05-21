from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from scfile.cli.cmd.convert import convert_command


runner = CliRunner()

MODEL = "model_v12.mcsb"
TEXTURE = "texture_dxt1.ol"
IMAGE = "image.mic"


def test_convert_single_file(assets: Path, temp: Path):
    src = assets / "cli" / MODEL
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0
    assert (temp / "model_v12.obj").exists()


def test_convert_mdlformat(assets: Path, temp: Path):
    src = assets / "cli" / MODEL
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "-F", "obj"])
    assert result.exit_code == 0
    assert (temp / "model_v12.obj").exists()
    assert not (temp / "model_v12.glb").exists()


def test_convert_skeleton(assets: Path, temp: Path):
    src = assets / "cli" / MODEL
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--skeleton"])
    assert result.exit_code == 0


def test_convert_animation(assets: Path, temp: Path):
    src = assets / "cli" / MODEL
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--animation"])
    assert result.exit_code == 0


def test_convert_on_conflict_rename(assets: Path, temp: Path):
    src = assets / "cli" / MODEL
    (temp / "model_v12.obj").write_text("existing")
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--on-conflict", "rename"])
    assert result.exit_code == 0
    assert (temp / "model_v12 (1).obj").exists()


def test_convert_on_conflict_skip(assets: Path, temp: Path):
    src = assets / "cli" / MODEL
    (temp / "model_v12.obj").write_text("existing")
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--on-conflict", "skip"])
    assert result.exit_code == 0
    assert (temp / "model_v12.obj").read_text() == "existing"


def test_convert_missing_file(temp: Path):
    result = runner.invoke(convert_command, [str(temp / "missing.mcsb")])
    assert result.exit_code != 0


def test_convert_texture(assets: Path, temp: Path):
    src = assets / "cli" / TEXTURE
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0
    assert list(temp.glob("*.dds"))


def test_convert_image(assets: Path, temp: Path):
    src = assets / "cli" / IMAGE
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0
    assert list(temp.glob("*.png"))


def test_relative(assets: Path, temp: Path):
    src = assets / "cli"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--relative"])
    assert result.exit_code == 0
    assert (temp / "sub" / "sub_model_v12.obj").exists()


def test_parent(assets: Path, temp: Path):
    src = assets / "cli"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--parent"])
    assert result.exit_code == 0
    assert (temp / "cli" / "sub" / "sub_model_v12.obj").exists()


def test_relative_flat_output(assets: Path, temp: Path):
    src = assets / "cli"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0
    assert (temp / "model_v12.obj").exists()
    assert (temp / "sub_model_v12.obj").exists()
    assert not (temp / "sub").exists()


def test_relative_with_parent(assets: Path, temp: Path):
    src = assets / "cli" / "sub"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--parent"])
    assert result.exit_code == 0
    assert (temp / "sub" / "sub_model_v12.obj").exists()


def test_parent_implies_relative(assets: Path, temp: Path):
    src = assets / "cli" / "sub"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "--parent"])
    assert result.exit_code == 0
    assert (temp / "sub" / "sub_model_v12.obj").exists()


def test_multiple_sources(assets: Path, temp: Path):
    src1 = assets / "cli" / MODEL
    src2 = assets / "cli" / TEXTURE
    result = runner.invoke(convert_command, [str(src1), str(src2), "-O", str(temp)])
    assert result.exit_code == 0
    assert (temp / "model_v12.obj").exists()
    assert list(temp.glob("*.dds"))


def test_overwrite_default(assets: Path, temp: Path):
    src = assets / "cli" / MODEL
    (temp / "model_v12.obj").write_text("old")
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0
    assert (temp / "model_v12.obj").read_text() != "old"


def test_default(assets: Path):
    src = assets / "cli" / MODEL
    with patch("scfile.cli.cmd.convert.convert.auto") as convert_auto:
        result = runner.invoke(convert_command, [str(src)])
        assert result.exit_code == 0
        convert_auto.assert_called_once()


def test_relative_no_output(assets: Path):
    src = assets / "cli" / MODEL
    with patch("scfile.cli.cmd.convert.convert.auto"):
        result = runner.invoke(convert_command, [str(src), "--relative"])
        assert result.exit_code == 0
        assert result.output


def test_skeleton_obj_warns(assets: Path, temp: Path):
    src = assets / "cli" / MODEL
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "-F", "obj", "--skeleton"])
    assert result.exit_code == 0


def test_animation_obj_warns(assets: Path, temp: Path):
    src = assets / "cli" / MODEL
    result = runner.invoke(convert_command, [str(src), "-O", str(temp), "-F", "obj", "--animation"])
    assert result.exit_code == 0


def test_invalid_structure_error(assets: Path, temp: Path):
    src = assets / "invalid" / "broken.ol"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0


def test_empty_file_error(assets: Path, temp: Path):
    src = assets / "invalid" / "empty.mic"
    result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
    assert result.exit_code == 0


def test_unexpected_error(assets: Path, temp: Path):
    src = assets / "cli" / MODEL
    with patch("scfile.cli.cmd.convert.convert.auto", side_effect=RuntimeError("boom")):
        result = runner.invoke(convert_command, [str(src), "-O", str(temp)])
        assert result.exit_code == 0
