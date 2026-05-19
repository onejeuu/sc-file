import pytest

from scfile import exceptions as E


@pytest.mark.parametrize(
    "exc, kwargs",
    [
        (E.BaseIOError, {}),
        (E.FileError, {"location": "file.bin"}),
        (E.FileNotFound, {"location": "file.bin"}),
        (E.EmptyFileError, {"location": "file.bin"}),
        (E.UnsupportedFormatError, {"location": "file.bin", "suffix": ".bin"}),
        (E.InvalidSignatureError, {"location": "file.bin", "actual": b"\x00", "expected": b"\x01"}),
        (E.InvalidStructureError, {"location": "file.bin"}),
        (E.InvalidStructureError, {"location": "file.bin", "position": 73}),
        (E.DecodingError, {}),
        (E.EncodingError, {}),
        (E.ParsingError, {}),
        (E.UnsupportedError, {}),
    ],
)
def test_exc_str(exc, kwargs):
    assert isinstance(str(exc(**kwargs)), str)
