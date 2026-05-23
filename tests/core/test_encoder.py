from io import BytesIO
from pathlib import Path

from scfile.core.content import ModelContent
from scfile.core.encoder import FileEncoder
from scfile.core.options import Options
from scfile.structures.models import Flag, ModelScene
from tests.conftest import DATA, OUTPUT, FakeContent, FakeEncoder, FakeModelEncoder


def test_encode_serializes_data():
    enc = FakeEncoder(FakeContent(parsed=DATA))
    enc.encode()
    assert enc.getvalue() == DATA
    enc.close()


def test_encode_returns_self():
    enc = FakeEncoder(FakeContent(parsed=DATA))
    assert enc.encode() is enc
    enc.close()


def test_encode_with_signature():
    class _Enc(FakeEncoder):
        signature = b"STRN"

    enc = _Enc(FakeContent(parsed=DATA))
    enc.encode()
    assert enc.getvalue() == b"STRN" + DATA


def test_ctx_cleared_on_close():
    enc = FakeEncoder(FakeContent())
    enc.ctx["key"] = "value"
    enc.close()
    assert enc.ctx == {}


def test_save_as(temp: Path):
    enc = FakeEncoder(FakeContent(parsed=DATA))
    enc.encode()
    path = temp / OUTPUT
    enc.save_as(path)
    assert path.read_bytes() == DATA
    enc.close()


def test_export_as(temp: Path):
    enc = FakeEncoder(FakeContent(parsed=DATA))
    enc.encode()
    enc.export_as(temp / "out")
    assert (temp / "out.obj").read_bytes() == DATA
    enc.close()


def test_save(temp: Path):
    enc = FakeEncoder(FakeContent(parsed=DATA))
    enc.encode()
    path = temp / OUTPUT
    enc.save(path)
    assert path.read_bytes() == DATA
    assert enc.closed


def test_export(temp: Path):
    enc = FakeEncoder(FakeContent(parsed=DATA))
    enc.encode()
    enc.export(temp / "out")
    assert (temp / "out.obj").read_bytes() == DATA
    assert enc.closed


def test_output_default_is_bytesio():
    enc = FakeEncoder(FakeContent())
    enc.write(DATA)
    assert enc.getvalue() == DATA
    enc.close()


def test_output_to_path(temp: Path):
    path = temp / OUTPUT
    enc = FakeEncoder(FakeContent(parsed=DATA), output=path)
    enc.encode()
    enc.close()
    assert path.read_bytes() == DATA


def test_output_to_bytesio():
    buf = BytesIO()
    enc = FakeEncoder(FakeContent(parsed=DATA), output=buf)
    enc.encode()
    result = enc.getvalue()
    enc.close()
    assert result == DATA


def test_default_output_is_bytesio():
    enc = FakeEncoder(FakeContent())
    assert isinstance(enc._stream, BytesIO)
    enc.close()


def test_prelude_called():
    log = []

    class _PreludeEncoder(FakeEncoder):
        def prelude(self):
            log.append("pre")

        def serialize(self):
            log.append("ser")
            super().serialize()

    enc = _PreludeEncoder(FakeContent(parsed=DATA))
    enc.encode()
    assert log == ["pre", "ser"]
    enc.close()


def test_skeleton_presented():
    data = ModelContent(
        scene=ModelScene(),
        flags={Flag.SKELETON: True},
    )
    opts = Options(skeleton=True)
    enc = FakeModelEncoder(data, options=opts)
    assert enc._skeleton_presented
    enc.close()


def test_skeleton_presented_flag_false():
    data = ModelContent(
        scene=ModelScene(),
        flags={Flag.SKELETON: False},
    )
    opts = Options(skeleton=True)
    enc = FakeModelEncoder(data, options=opts)
    assert not enc._skeleton_presented
    enc.close()


def test_skeleton_presented_option_false():
    data = ModelContent(
        scene=ModelScene(),
        flags={Flag.SKELETON: True},
    )
    opts = Options(skeleton=False)
    enc = FakeModelEncoder(data, options=opts)
    assert not enc._skeleton_presented
    enc.close()


def test_animation_presented():
    data = ModelContent(
        scene=ModelScene(),
        flags={Flag.SKELETON: True},
    )
    opts = Options(skeleton=True, animation=True)
    enc = FakeModelEncoder(data, options=opts)
    assert enc._animation_presented
    enc.close()


def test_animation_presented_no_animation_option():
    data = ModelContent(
        scene=ModelScene(),
        flags={Flag.SKELETON: True},
    )
    opts = Options(skeleton=True, animation=False)
    enc = FakeModelEncoder(data, options=opts)
    assert not enc._animation_presented
    enc.close()


def test_skeleton_presented_on_non_model():
    enc = FakeEncoder(FakeContent())
    assert not enc._skeleton_presented
    enc.close()


def test_animation_presented_on_non_model():
    enc = FakeEncoder(FakeContent())
    assert not enc._animation_presented
    enc.close()


def test_transform_called_on_model():
    log = []

    def tf(scene):
        log.append("ok")
        return scene

    class _TfEncoder(FileEncoder[ModelContent]):
        transforms = [tf]

        def serialize(self):
            pass

    data = ModelContent(scene=ModelScene())
    enc = _TfEncoder(data)
    enc.encode()
    assert log == ["ok"]
    enc.close()


def test_transform_overridden():
    log = []

    def tf(scene):
        log.append("ok")
        return scene

    data = ModelContent(scene=ModelScene())
    enc = FakeModelEncoder(data)
    enc.encode(transforms=[tf])
    assert log == ["ok"]
    enc.close()
