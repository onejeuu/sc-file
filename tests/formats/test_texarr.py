import zipfile
from io import BytesIO

from scfile.formats.texarr import TexarrDecoder
from scfile.formats.zip import TexarrEncoder

from .conftest import extract


def test_texarr():
    src = "texarr/texarr"
    out = "texarr/texarr"
    source, output = extract(TexarrDecoder, TexarrEncoder, src, out)

    with zipfile.ZipFile(BytesIO(source)) as z1, zipfile.ZipFile(BytesIO(output)) as z2:
        assert z1.namelist() == z2.namelist()
        for name in z1.namelist():
            assert z1.read(name) == z2.read(name)
