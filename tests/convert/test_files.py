from pathlib import Path

import pytest

from scfile import exceptions
from scfile.convert import files, manual
from scfile.enums import FileFormat
from scfile.options import Options
from scfile.registry import Registry, Resolver
from tests.conftest import BytesDecoder, BytesEncoder


class PngEncoder(BytesEncoder):
    format = FileFormat.PNG


class PngDecoder(BytesDecoder):
    format = FileFormat.PNG


class BrokenEncoder(PngEncoder):
    def _serialize(self) -> None:
        self.io.write(b"partial")
        raise RuntimeError


class InterruptedEncoder(PngEncoder):
    def _serialize(self) -> None:
        self.io.write(b"partial")
        raise KeyboardInterrupt


def test_manual_writes_path(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")

    result = manual(BytesDecoder, PngEncoder, source, output)

    assert PngEncoder.suffix() == ".png"
    assert result == output
    assert output.read_bytes() == b"HXGNdata"


def test_manual_returns_none_when_skipped(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")
    output.write_bytes(b"existing")

    result = manual(BytesDecoder, PngEncoder, source, output, Options(on_conflict="skip"))

    assert result is None
    assert output.read_bytes() == b"existing"


def test_manual_renames_conflicting_output(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")
    output.write_bytes(b"existing")

    result = manual(BytesDecoder, PngEncoder, source, output, Options(on_conflict="rename"))

    assert result == tmp_path / "output (1).png"
    assert result is not None
    assert output.read_bytes() == b"existing"
    assert result.read_bytes() == b"HXGNdata"


def test_manual_removes_failed_output(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")

    with pytest.raises(RuntimeError):
        manual(BytesDecoder, BrokenEncoder, source, output)

    assert not output.exists()
    assert not list(tmp_path.glob(".output.png.*.tmp"))


def test_manual_keeps_previous_output(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")
    output.write_bytes(b"previous")

    with pytest.raises(RuntimeError):
        manual(BytesDecoder, BrokenEncoder, source, output)

    assert output.read_bytes() == b"previous"
    assert not list(tmp_path.glob(".output.png.*.tmp"))


def test_manual_removes_interrupted_output(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")

    with pytest.raises(KeyboardInterrupt):
        manual(BytesDecoder, InterruptedEncoder, source, output)

    assert not output.exists()
    assert not list(tmp_path.glob(".output.png.*.tmp"))


def test_format() -> None:
    assert files.format("model.mcsb") == "mcsb"
    assert files.format("model.custom") == "custom"


def test_auto_uses_resolved_handlers(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")

    registry = Registry(PngDecoder, PngEncoder)
    resolver = Resolver(registry)
    monkeypatch.setattr(files, "RESOLVER", resolver)
    monkeypatch.setattr(files, "REGISTRY", registry)

    result = files.auto(source, output)

    assert result == output
    assert output.read_bytes() == b"HXGNdata"


def test_auto_rejects_unknown_format(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "source.unknown"
    source.write_bytes(b"data")
    registry = Registry()
    resolver = Resolver(registry)
    monkeypatch.setattr(files, "RESOLVER", resolver)
    monkeypatch.setattr(files, "REGISTRY", registry)

    with pytest.raises(exceptions.UnknownFormatError):
        files.auto(source)


def test_auto_requires_target(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    source.write_bytes(b"STRNdata")

    registry = Registry(PngDecoder)
    resolver = Resolver(registry)
    monkeypatch.setattr(files, "RESOLVER", resolver)
    monkeypatch.setattr(files, "REGISTRY", registry)

    with pytest.raises(exceptions.ConversionError):
        files.auto(source)
