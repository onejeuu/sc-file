from scfile.structures.textures import CubemapTexture, DefaultTexture


def test_texture():
    tex = DefaultTexture(mipmaps=[b"a", b"b", b"c"])
    assert tex.image == b"abc"


def test_texture_empty():
    tex = DefaultTexture()
    assert tex.image == b""


def test_linear_size():
    tex = DefaultTexture(uncompressed=[4096, 1024, 256])
    assert tex.linear_size == 4096


def test_cubemap():
    tex = CubemapTexture(faces=[[b"a"], [b"b"], [b"c"], [b"d"], [b"e"], [b"f"]])
    assert tex.image == b"abcdef"


def test_cubemap_linear_size():
    tex = CubemapTexture(uncompressed=[[512, 128], [512, 128]])
    assert tex.linear_size == 512
