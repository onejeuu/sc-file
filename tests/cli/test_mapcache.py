from pathlib import Path

from click.testing import CliRunner

from scfile.cli.cmd.mapcache import mapcache_command
from tests.conftest import ASSETS


runner = CliRunner()


def test_mapcache(temp: Path):
    src = ASSETS / "cli" / "mapcache"
    result = runner.invoke(mapcache_command, [str(src), "-O", str(temp), "-W", "0"])
    assert result.exit_code == 0
    assert (temp / "r.0.0.mca").exists()


def test_mapcache_auto_output(temp: Path):
    src = temp / "mapcache"
    src.mkdir()
    (src / "r.0.0.mdat").write_bytes((ASSETS / "cli" / "mapcache" / "r.0.0.mdat").read_bytes())

    result = runner.invoke(mapcache_command, [str(src)])
    assert result.exit_code == 0
    assert (src.parent / "mapcache_mca").is_dir()


def test_mapcache_multithread(temp: Path):
    src = ASSETS / "cli" / "mapcache"
    result = runner.invoke(mapcache_command, [str(src), "-O", str(temp), "-W", "2"])
    assert result.exit_code == 0


def test_mapcache_empty_dir(temp: Path):
    empty = temp / "empty"
    empty.mkdir()
    result = runner.invoke(mapcache_command, [str(empty)])
    assert result.exit_code == 0


def test_mapcache_no_valid_regions(temp: Path):
    bad = temp / "bad"
    bad.mkdir()
    (bad / "reg.0.0.mdat").write_bytes(b"\x00")
    result = runner.invoke(mapcache_command, [str(bad)])
    assert result.exit_code == 0


def test_mapcache_existing_backup(temp: Path):
    src = ASSETS / "cli" / "mapcache"
    out = temp / "out"
    out.mkdir()
    (out / "r.0.0.mca").write_bytes(b"old")
    result = runner.invoke(mapcache_command, [str(src), "-O", str(out), "-W", "0"])
    assert result.exit_code == 0


def test_mapcache_invalid_filename(temp: Path):
    src = temp / "mixed"
    src.mkdir()
    (src / "r.0.0.mdat").write_bytes((ASSETS / "cli" / "mapcache" / "r.0.0.mdat").read_bytes())
    (src / "INVALID_NAME.mdat").write_bytes(b"\x00")
    result = runner.invoke(mapcache_command, [str(src), "-O", str(temp), "-W", "0"])
    assert result.exit_code == 0
    assert (temp / "r.0.0.mca").exists()


def test_mapcache_all_invalid_filenames(temp: Path):
    src = temp / "invalid"
    src.mkdir()
    (src / "INVALID_NAME.mdat").write_bytes(b"\x00")
    (src / "INVALID_NAME_BROTHER.mdat").write_bytes(b"\x00")
    result = runner.invoke(mapcache_command, [str(src)])
    assert result.exit_code == 0
