import pytest

from scfile.content import RegionContent, TextureContent
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


def test_deprecated_texture_aliases() -> None:
    content = TextureContent()

    with pytest.deprecated_call():
        content.mipmap_count = 3
    with pytest.deprecated_call():
        content.format = b"DXT1"
    with pytest.deprecated_call():
        content.path_hash = b"path"

    assert content.meta == TextureMeta(3, b"DXT1", b"path")

    with pytest.deprecated_call():
        assert content.mipmap_count == 3
    with pytest.deprecated_call():
        assert content.format == b"DXT1"
    with pytest.deprecated_call():
        assert content.path_hash == b"path"


def test_deprecated_region_aliases() -> None:
    content = RegionContent()

    with pytest.deprecated_call():
        content.rx = 1
    with pytest.deprecated_call():
        content.rz = -2
    with pytest.deprecated_call():
        content.sector_offsets = [3]
    with pytest.deprecated_call():
        content.sector_counts = [4]

    assert (content.x, content.z, content.offsets, content.counts) == (1, -2, [3], [4])

    with pytest.deprecated_call():
        assert content.rx == 1
    with pytest.deprecated_call():
        assert content.rz == -2
    with pytest.deprecated_call():
        assert content.sector_offsets == [3]
    with pytest.deprecated_call():
        assert content.sector_counts == [4]
