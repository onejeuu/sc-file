from scfile.content.textures import CubemapTexture, DefaultTexture


def test_image() -> None:
    texture = DefaultTexture(mipmaps=[b"a", b"b", b"c"])

    assert texture.image == b"abc"
    assert texture.mipmap_count == 3


def test_linear_size() -> None:
    texture = DefaultTexture(uncompressed=[4096, 1024, 256])

    assert texture.linear_size == 4096


def test_cubemap_image() -> None:
    texture = CubemapTexture(
        faces=[
            [b"a", b"1"],
            [b"b", b"2"],
            [b"c", b"3"],
            [b"d", b"4"],
            [b"e", b"5"],
            [b"f", b"6"],
        ]
    )

    assert texture.image == b"a1b2c3d4e5f6"
    assert texture.mipmap_count == 2


def test_cubemap_size() -> None:
    texture = CubemapTexture(uncompressed=[[512, 128]])

    assert texture.linear_size == 512
