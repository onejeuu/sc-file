import pytest

from tools.cmd.audit import config


def test_read_missing_config_is_empty(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(config, "CONFIG", tmp_path / "missing.toml")

    assert config.read() == {}


def test_resolve_cli_values_override_config(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(config, "read", lambda: {"path": "config-root", "workers": 8, "animation": False})

    result = config.resolve(tmp_path, ("nbt",), (), 1, True, True, None)

    assert result.root == tmp_path.resolve()
    assert result.formats == ("nbt",)
    assert result.workers == 1
    assert result.animation is True
    assert result.mdat_extended is True


def test_resolve_rejects_negative_config_workers(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(config, "read", lambda: {"workers": -1})

    with pytest.raises(config.click.UsageError, match="workers"):
        config.resolve(tmp_path, (), (), None, None, None)
