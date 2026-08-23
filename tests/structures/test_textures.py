from scfile.content.textures import CubemapTexture, DefaultTexture


def test_image() -> None:
    texture = DefaultTexture(mipmaps=[b"a", b"b", b"c"])

    assert texture.image == b"abc"


def test_linear_size() -> None:
    texture = DefaultTexture(uncompressed=[4096, 1024, 256])

    assert texture.linear_size == 4096


def test_cubemap_image() -> None:
    texture = CubemapTexture(faces=[[b"a"], [b"b"], [b"c"], [b"d"], [b"e"], [b"f"]])

    assert texture.image == b"abcdef"


def test_cubemap_size() -> None:
    texture = CubemapTexture(uncompressed=[[512, 128]])

    assert texture.linear_size == 512
