import zipfile
from io import BytesIO
from pathlib import Path

from scfile.formats.texarr import TextureArrayDecoder
from scfile.formats.zip import TextureArrayEncoder

from .conftest import extract


def test_texarr(assets: Path):
    source, output = extract(TextureArrayDecoder, TextureArrayEncoder, assets, "texarr/texarr", "texarr/texarr")

    with zipfile.ZipFile(BytesIO(source)) as z1, zipfile.ZipFile(BytesIO(output)) as z2:
        assert z1.namelist() == z2.namelist()
        for name in z1.namelist():
            assert z1.read(name) == z2.read(name)
