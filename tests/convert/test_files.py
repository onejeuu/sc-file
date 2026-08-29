from pathlib import Path

import pytest

from scfile import exceptions
from scfile.convert import files, manual
from scfile.enums import FileFormat, OnConflict
from scfile.formats import DdsEncoder, OlDecoder
from scfile.formats.registry import Registry
from scfile.options import Options
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


def test_manual(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")

    result = manual(BytesDecoder, PngEncoder, source, output)

    assert PngEncoder.suffix() == ".png"
    assert result == output
    assert output.read_bytes() == b"HXGNdata"


def test_manual_skip(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")
    output.write_bytes(b"existing")

    result = manual(BytesDecoder, PngEncoder, source, output, Options(on_conflict=OnConflict.SKIP))

    assert result is None
    assert output.read_bytes() == b"existing"


def test_manual_rename(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")
    output.write_bytes(b"existing")

    result = manual(BytesDecoder, PngEncoder, source, output, Options(on_conflict=OnConflict.RENAME))

    assert result == tmp_path / "output (1).png"
    assert result is not None
    assert output.read_bytes() == b"existing"
    assert result.read_bytes() == b"HXGNdata"


def test_manual_failure(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")

    with pytest.raises(RuntimeError):
        manual(BytesDecoder, BrokenEncoder, source, output)

    assert not output.exists()
    assert not list(tmp_path.glob(".output.png.*.tmp"))


def test_manual_preserves_output(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")
    output.write_bytes(b"previous")

    with pytest.raises(RuntimeError):
        manual(BytesDecoder, BrokenEncoder, source, output)

    assert output.read_bytes() == b"previous"
    assert not list(tmp_path.glob(".output.png.*.tmp"))


def test_manual_interrupt(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")

    with pytest.raises(KeyboardInterrupt):
        manual(BytesDecoder, InterruptedEncoder, source, output)

    assert not output.exists()
    assert not list(tmp_path.glob(".output.png.*.tmp"))


def test_manual_texture_metadata(tmp_path: Path) -> None:
    source = Path(__file__).parents[1] / "assets/formats/textures/source/texture_dxt1.ol"
    output = tmp_path / "texture.dds"

    with pytest.raises(exceptions.ConversionError, match="without mipmaps"):
        manual(OlDecoder, DdsEncoder, source, output, Options(max_mipmaps=0))

    assert not output.exists()


def test_format() -> None:
    assert files.format("model.mcsb") == "mcsb"
    assert files.format("model.custom") == "custom"


def test_auto(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")

    catalog = Registry((PngDecoder,), (PngEncoder,), {})
    monkeypatch.setattr(files, "registry", catalog)

    result = files.auto(source, output, Options(targets={BytesDecoder.content_type: FileFormat.PNG}))

    assert result == output
    assert output.read_bytes() == b"HXGNdata"


def test_auto_unknown(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "source.unknown"
    source.write_bytes(b"data")
    catalog = Registry((), (), {})
    monkeypatch.setattr(files, "registry", catalog)

    with pytest.raises(exceptions.UnknownFormatError):
        files.auto(source)


def test_auto_target(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    source.write_bytes(b"STRNdata")

    catalog = Registry((PngDecoder,), (), {})
    monkeypatch.setattr(files, "registry", catalog)

    with pytest.raises(exceptions.ConversionError):
        files.auto(source, options=Options(targets={BytesDecoder.content_type: FileFormat.PNG}))
