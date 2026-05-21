from pathlib import Path

from click.testing import CliRunner

from scfile.cli.cmd.mapcache import mapcache_command
from tests.conftest import ASSETS


runner = CliRunner()


def test_mapcache(temp: Path):
    src = ASSETS / "cli/mapcache"
    result = runner.invoke(mapcache_command, [str(src), "-O", str(temp), "-W", "0"])
    assert result.exit_code == 0
    assert (temp / "r.0.0.mca").exists()
