from pathlib import Path

import pytest

from tools.cmd import tools


COMMANDS = ("audit", "info", "mapcache", "mappings", "profile")


@pytest.mark.parametrize("command", COMMANDS)
def test_command_help_is_available(runner, command: str) -> None:
    result = runner.invoke(tools, [command, "--help"])

    assert result.exit_code == 0, result.output
    assert "Usage:" in result.output


def test_root_help_is_available(runner) -> None:
    result = runner.invoke(tools, ["--help"])

    assert result.exit_code == 0, result.output
    for command in COMMANDS:
        assert command in result.output


def test_info_rejects_unsupported_source(runner, tmp_path: Path) -> None:
    source = tmp_path / "unknown.bin"
    source.write_bytes(b"data")

    result = runner.invoke(tools, ["info", str(source)])

    assert result.exit_code == 2
    assert "Unsupported source format" in result.output


def test_profile_rejects_unsupported_target(runner, tmp_path: Path) -> None:
    source = tmp_path / "model.mcsb"
    source.write_bytes(b"not decoded")

    # The command must fail during target validation, before it can create reports.
    result = runner.invoke(tools, ["profile", str(source), "-T", "unknown", "--reports", str(tmp_path / "reports")])

    assert result.exit_code == 2
    assert "Unsupported conversion" in result.output
    assert not (tmp_path / "reports").exists()
