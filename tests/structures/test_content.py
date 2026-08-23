from scfile.content import TextureContent
from scfile.content.textures import CubemapTexture, DefaultTexture


def test_cubemap() -> None:
    assert TextureContent(texture=CubemapTexture()).is_cubemap
    assert not TextureContent(texture=DefaultTexture()).is_cubemap


def test_fourcc() -> None:
    assert TextureContent(format=b"DXN_X").fourcc == b"ATI1"
    assert TextureContent(format=b"DXN_XY").fourcc == b"ATI2"
    assert TextureContent(format=b"RGBA32F").fourcc == b"DX10"


def test_compressed() -> None:
    assert TextureContent(format=b"DXT1").is_compressed
    assert TextureContent(format=b"DXN_X").is_compressed
    assert not TextureContent(format=b"RAW").is_compressed
