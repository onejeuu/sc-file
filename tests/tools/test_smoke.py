from pathlib import Path

import pytest

from tools.cmd import tools


@pytest.mark.parametrize(
    "flags",
    [
        (),
        ("--animation",),
        ("--stats",),
        ("--animation", "--stats"),
    ],
)
def test_audit_smoke_runs_empty_tree(runner, tmp_path: Path, flags: tuple[str, ...], monkeypatch) -> None:
    import importlib

    audit = importlib.import_module("tools.cmd.audit.audit")

    monkeypatch.setattr(audit, "REPORTS", tmp_path / "reports")
    result = runner.invoke(tools, ["audit", str(tmp_path), "-F", "mcsb", *flags])

    assert result.exception is None, result.output
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("info",), "Missing argument"),
        (("mapcache", "region"), "Missing argument"),
        (("mapcache", "chunk", "dummy"), "does not exist"),
        (
            (
                "mappings",
                "--stalcraft-texarr",
                "missing.texarr",
                "--minecraft-jar",
                "missing.jar",
            ),
            "source file not found",
        ),
    ],
)
def test_tool_commands_reach_validation(runner, args: tuple[str, ...], message: str) -> None:
    result = runner.invoke(tools, list(args))

    assert result.exit_code != 0
    assert message.casefold() in result.output.casefold()


def test_profile_smoke_reaches_target_validation(runner, tmp_path: Path) -> None:
    source = tmp_path / "model.mcsb"
    source.write_bytes(b"not a model")

    result = runner.invoke(tools, ["profile", str(source), "-T", "unknown", "--reports", str(tmp_path / "reports")])

    assert result.exit_code == 2
    assert "Unsupported conversion" in result.output
    assert not (tmp_path / "reports").exists()
