from io import BytesIO
from zipfile import ZipFile

from scfile.formats import TexarrDecoder, ZipEncoder

from .conftest import ASSETS, export


def test_texarr_roundtrips_archive() -> None:
    root = ASSETS / "archive"
    actual = export(TexarrDecoder, ZipEncoder, root / "source" / "textures.texarr")
    expected = (root / "zip" / "textures.zip").read_bytes()

    with ZipFile(BytesIO(actual)) as result, ZipFile(BytesIO(expected)) as reference:
        assert result.namelist() == reference.namelist()
        for name in result.namelist():
            assert result.read(name) == reference.read(name)
