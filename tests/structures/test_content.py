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


@pytest.mark.parametrize(
    ("content", "alias", "target", "value"),
    (
        (TextureContent(), "mipmap_count", "meta.mipmap_count", 3),
        (TextureContent(), "format", "meta.format", b"DXT1"),
        (TextureContent(), "path_hash", "meta.path_hash", b"path"),
        (RegionContent(), "rx", "x", 1),
        (RegionContent(), "rz", "z", -2),
        (RegionContent(), "sector_offsets", "offsets", [3]),
        (RegionContent(), "sector_counts", "counts", [4]),
    ),
)
def test_aliases(content, alias: str, target: str, value) -> None:
    with pytest.deprecated_call():
        setattr(content, alias, value)

    parent, _, attribute = target.rpartition(".")
    owner = getattr(content, parent) if parent else content
    assert getattr(owner, attribute) == value

    with pytest.deprecated_call():
        assert getattr(content, alias) == value
