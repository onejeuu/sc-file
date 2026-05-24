from scfile import exceptions
from scfile.formats.mcsa.exceptions import McsaCountsLimit, McsaVersionUnsupported
from scfile.formats.ms3d.exceptions import Ms3dCountsLimit
from scfile.formats.ol.exceptions import OlFormatUnsupported


def test_strings():
    assert str(exceptions.FileNotFound("test.txt"))
    assert str(exceptions.UnsupportedFormatError("test.txt", ".xyz"))
    assert str(exceptions.InvalidSignatureError("test.txt", b"\x00", b"\x01"))
    assert str(exceptions.RegionFileError("reg.0.0.mdat"))
    assert str(exceptions.MergeInterrupted())
    assert str(McsaCountsLimit("model.mcsa", "vertices", 0x7FFFFFFF))
    assert str(McsaVersionUnsupported("model.mcsa", 99.0))
    assert str(Ms3dCountsLimit("vertices", 0x7FFFFFFF, 512))
    assert str(OlFormatUnsupported("texture.ol", b"\x00\x00\x00\x00"))
