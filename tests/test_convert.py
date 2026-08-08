from pathlib import Path

from scfile.convert import manual
from scfile.enums import FileFormat
from scfile.options import Options

from tests.conftest import BytesDecoder, BytesEncoder


class PngEncoder(BytesEncoder):
    format = FileFormat.PNG


def test_manual_writes_path(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.png"
    source.write_bytes(b"STRNdata")

    result = manual(BytesDecoder, PngEncoder, source, output)

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
