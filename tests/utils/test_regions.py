import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scfile import exceptions
from scfile.core import RegionContent
from scfile.utils.regions import merge, parse, resolve


def test_parse():
    paths = [
        Path("r.0.0.mdat"),
        Path("reg.1.-1.mdat"),
        Path("r.2.3.mdat"),
        Path("invalid.mdat"),
        Path("r.4.5.extra.mdat"),
    ]
    result = parse(paths)

    assert result == {(0, 0): [Path("r.0.0.mdat")], (1, -1): [Path("reg.1.-1.mdat")], (2, 3): [Path("r.2.3.mdat")]}


def test_parse_empty():
    assert parse([]) == {}


def test_parse_all_invalid():
    assert parse([Path("bad.mdat"), Path("also_bad.mdat")]) == {}


def test_resolve(temp: Path):
    src = temp / "mdats"
    src.mkdir()
    (src / "r.0.0.mdat").write_bytes(b"\x00")
    (src / "r.1.0.mdat").write_bytes(b"\x00")
    (src / "empty.mdat").write_bytes(b"")
    (src / "skip.bck.mdat").write_bytes(b"\x00")
    (src / "sub").mkdir()
    (src / "sub" / "r.2.0.mdat").write_bytes(b"\x00")

    result = resolve(src)
    names = {p.name for p in result}
    assert names == {"r.0.0.mdat", "r.1.0.mdat", "r.2.0.mdat"}


def test_resolve_empty(temp: Path):
    src = temp / "empty"
    src.mkdir()
    assert resolve(src) == []


def test_merge_interrupted():
    cancelled = threading.Event()
    cancelled.set()

    with patch("scfile.formats.mdat.MdatDecoder") as mdat:
        region = RegionContent()
        region.chunks = []
        mdat.return_value.__enter__.return_value.decode.return_value = region

        with pytest.raises(exceptions.MergeInterrupted):
            merge(
                key=(0, 0),
                paths=[Path("r.0.0.mdat")],
                output=Path("out"),
                options=MagicMock(),
                cancelled=cancelled,
            )


def test_merge_region_file_error():
    with patch("scfile.formats.mdat.MdatDecoder") as mdat:
        mdat.return_value.__enter__.return_value.decode.side_effect = Exception("fail")

        with pytest.raises(exceptions.RegionFileError):
            merge(
                key=(0, 0),
                paths=[Path("r.0.0.mdat")],
                output=Path("out"),
                options=MagicMock(),
                cancelled=None,
            )
