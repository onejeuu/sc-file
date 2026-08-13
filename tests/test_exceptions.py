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


def test_handler_state_context() -> None:
    operation = "decode"
    error = exceptions.HandlerStateError(operation, HandlerState.FAILED, closed=True)

    assert error.operation == operation
    assert error.state is HandlerState.FAILED
    assert error.closed


def test_unsupported_errors() -> None:
    assert exceptions.ModelVersionError.unsupported
    assert exceptions.TextureFormatError.unsupported
    assert exceptions.TextureKindError.unsupported
    assert not exceptions.BinaryStructureError.unsupported
