from scfile.content import TextureContent
from scfile.content.textures import CubemapTexture, DefaultTexture, TextureMeta


def test_cubemap() -> None:
    assert TextureContent(texture=CubemapTexture()).is_cubemap
    assert not TextureContent(texture=DefaultTexture()).is_cubemap


def test_texture_metadata() -> None:
    content = TextureContent(
        meta=TextureMeta(mipmap_count=3),
        texture=DefaultTexture(mipmaps=[b"base"]),
    )

    assert content.meta.mipmap_count == 3
    assert content.texture.mipmap_count == 1


def test_fourcc() -> None:
    assert TextureContent(meta=TextureMeta(format=b"DXN_X")).fourcc == b"ATI1"
    assert TextureContent(meta=TextureMeta(format=b"DXN_XY")).fourcc == b"ATI2"
    assert TextureContent(meta=TextureMeta(format=b"RGBA32F")).fourcc == b"DX10"


def test_compressed() -> None:
    assert TextureContent(meta=TextureMeta(format=b"DXT1")).is_compressed
    assert TextureContent(meta=TextureMeta(format=b"DXN_X")).is_compressed
    assert not TextureContent(meta=TextureMeta(format=b"RAW")).is_compressed
