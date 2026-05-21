from unittest.mock import patch

from click.testing import CliRunner

from scfile.cli import scfile
from scfile.enums import UpdateStatus
from scfile.utils.updates import UpdateCheck


runner = CliRunner()


def test_version_flag():
    result = runner.invoke(scfile, ["--version"])
    assert result.exit_code == 0


def test_updates_flag():
    with patch("scfile.utils.cli.updates.check", return_value=UpdateCheck(UpdateStatus.UPTODATE, "", "")):
        result = runner.invoke(scfile, ["--updates"])
        assert result.exit_code == 0
