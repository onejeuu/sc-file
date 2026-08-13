from scfile import exceptions
from scfile.enums import HandlerState


def test_exception_context() -> None:
    subject = "vertices"
    location = "model.mcsb"
    error = exceptions.SafetyLimitError(
        subject,
        2_000_000,
        1_000_000,
        location=location,
        offset=42,
    )

    assert error.subject == subject
    assert error.count == 2_000_000
    assert error.maximum == 1_000_000
    assert error.location == location
    assert error.offset == 42


def test_handler_state() -> None:
    operation = "decode"
    error = exceptions.HandlerStateError(operation, HandlerState.FAILED, closed=True)

    assert error.operation == operation
    assert error.state is HandlerState.FAILED
    assert error.closed


def test_unsupported() -> None:
    assert exceptions.ModelVersionError.unsupported
    assert exceptions.TextureFormatError.unsupported
    assert exceptions.TextureKindError.unsupported
    assert not exceptions.BinaryStructureError.unsupported


def test_format_errors() -> None:
    model_version = exceptions.ModelVersionError(15, location="model.mcsb")
    texture_format = exceptions.TextureFormatError(b"DXT0", location="texture.ol", offset=4)
    texture_kind = exceptions.TextureKindError(7, location="texture.ol")
    signature = exceptions.SignatureMismatchError(b"BAD", b"MIC", location="image.mic")

    assert model_version.version == 15
    assert texture_format.format == b"DXT0"
    assert texture_format.location == "texture.ol"
    assert texture_format.offset == 4
    assert texture_kind.kind == 7
    assert signature.actual == b"BAD"
    assert signature.expected == b"MIC"


def test_merge_interrupted() -> None:
    assert isinstance(exceptions.MergeInterrupted(), exceptions.RegionError)
