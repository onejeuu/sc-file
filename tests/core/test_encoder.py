from io import BytesIO
from pathlib import Path

from scfile.core.content import ModelContent
from scfile.core.encoder import FileEncoder
from scfile.core.options import UserOptions
from scfile.structures.models import Flag, ModelScene

from .conftest import FakeContent, FakeEncoder, FakeModelEncoder


def test_encode_serializes_data():
    enc = FakeEncoder(FakeContent(parsed=b"hello"))
    enc.encode()
    assert enc.getvalue() == b"HXGNhello"
    enc.close()


def test_encode_returns_self():
    enc = FakeEncoder(FakeContent(parsed=b"x"))
    assert enc.encode() is enc
    enc.close()


def test_encode_without_signature():
    class _NoSigEncoder(FileEncoder[FakeContent]):
        format = FakeEncoder.format
        signature = None

        def serialize(self) -> None:
            self.write(b"raw")

    enc = _NoSigEncoder(FakeContent())
    enc.encode()
    assert enc.getvalue() == b"raw"
    enc.close()


def test_ctx_cleared_on_close():
    enc = FakeEncoder(FakeContent())
    enc.ctx["key"] = "value"
    enc.close()
    assert enc.ctx == {}


def test_save_as(temp: Path):
    enc = FakeEncoder(FakeContent(parsed=b"data"))
    enc.encode()
    path = temp / "out.obj"
    enc.save_as(path)
    assert path.read_bytes() == b"HXGNdata"
    enc.close()


def test_export_as(temp: Path):
    enc = FakeEncoder(FakeContent(parsed=b"x"))
    enc.encode()
    enc.export_as(temp / "out")
    assert (temp / "out.obj").read_bytes() == b"HXGNx"
    enc.close()


def test_save(temp: Path):
    enc = FakeEncoder(FakeContent(parsed=b"x"))
    enc.encode()
    path = temp / "out.obj"
    enc.save(path)
    assert path.read_bytes() == b"HXGNx"
    assert enc.closed


def test_export(temp: Path):
    enc = FakeEncoder(FakeContent(parsed=b"x"))
    enc.encode()
    enc.export(temp / "out")
    assert (temp / "out.obj").read_bytes() == b"HXGNx"
    assert enc.closed


def test_output_default_is_bytesio():
    enc = FakeEncoder(FakeContent())
    enc.write(b"test")
    assert enc.getvalue() == b"test"
    enc.close()


def test_output_to_path(temp: Path):
    path = temp / "direct.obj"
    enc = FakeEncoder(FakeContent(parsed=b"direct"), output=path)
    enc.encode()
    enc.close()
    assert path.read_bytes() == b"HXGNdirect"


def test_output_to_bytesio():
    buf = BytesIO()
    enc = FakeEncoder(FakeContent(parsed=b"buf"), output=buf)
    enc.encode()
    result = enc.getvalue()
    enc.close()
    assert result == b"HXGNbuf"


def test_default_output_is_bytesio():
    enc = FakeEncoder(FakeContent())
    assert isinstance(enc._stream, BytesIO)
    enc.close()


def test_suffix():
    enc = FakeEncoder(FakeContent())
    assert enc.suffix == ".obj"
    enc.close()


def test_prelude_called():
    log = []

    class _PreludeEncoder(FakeEncoder):
        def prelude(self):
            log.append("pre")

        def serialize(self):
            log.append("ser")
            super().serialize()

    enc = _PreludeEncoder(FakeContent(parsed=b"x"))
    enc.encode()
    assert log == ["pre", "ser"]
    enc.close()


def test_skeleton_presented():
    data = ModelContent(
        scene=ModelScene(),
        flags={Flag.SKELETON: True},
    )
    opts = UserOptions(parse_skeleton=True)
    enc = FakeModelEncoder(data, options=opts)
    assert enc._skeleton_presented
    enc.close()


def test_skeleton_presented_flag_false():
    data = ModelContent(
        scene=ModelScene(),
        flags={Flag.SKELETON: False},
    )
    opts = UserOptions(parse_skeleton=True)
    enc = FakeModelEncoder(data, options=opts)
    assert not enc._skeleton_presented
    enc.close()


def test_skeleton_presented_option_false():
    data = ModelContent(
        scene=ModelScene(),
        flags={Flag.SKELETON: True},
    )
    opts = UserOptions(parse_skeleton=False)
    enc = FakeModelEncoder(data, options=opts)
    assert not enc._skeleton_presented
    enc.close()


def test_animation_presented():
    data = ModelContent(
        scene=ModelScene(),
        flags={Flag.SKELETON: True},
    )
    opts = UserOptions(parse_skeleton=True, parse_animation=True)
    enc = FakeModelEncoder(data, options=opts)
    assert enc._animation_presented
    enc.close()


def test_animation_presented_no_animation_option():
    data = ModelContent(
        scene=ModelScene(),
        flags={Flag.SKELETON: True},
    )
    opts = UserOptions(parse_skeleton=True, parse_animation=False)
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
