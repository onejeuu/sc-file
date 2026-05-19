from scfile.core import content as C
from scfile.structures.textures import CubemapTexture, DefaultTexture


def test_reset_factory():
    c = C.ModelContent(version=99.0)
    c.reset()
    assert c.version == 0.0
    assert c.type == C.FileType.MODEL


def test_reset_value():
    c = C.ImageContent(image=b"data")
    c.reset()
    assert c.image == b""


def test_cubemap():
    assert C.TextureContent(texture=CubemapTexture()).is_cubemap
    assert not C.TextureContent(texture=DefaultTexture()).is_cubemap


def test_compressed():
    assert C.TextureContent(format=b"DXT1").is_compressed
    assert not C.TextureContent(format=b"RAW").is_compressed


def test_fourcc():
    assert C.TextureContent(format=b"DXN_XY").fourcc == b"ATI2"
    assert C.TextureContent(format=b"RGBA32F").fourcc == b"DX10"
    assert C.TextureContent(format=b"DXT5").fourcc == b"DXT5"
