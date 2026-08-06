import pytest

from scfile.enums import HandlerState
from scfile import exceptions


@pytest.mark.parametrize(
    "error",
    (
        exceptions.HandlerStateError("decode", HandlerState.FAILED),
        exceptions.FileNotFound("file"),
        exceptions.EmptyFileError("file"),
        exceptions.UnknownFormatError("file", ".unknown"),
        exceptions.ModelVersionError(99.0),
        exceptions.TextureFormatError(b"unknown"),
        exceptions.TextureKindError(99),
        exceptions.SignatureMismatchError(b"bad", b"MIC"),
        exceptions.BinaryStructureError(),
        exceptions.SafetyLimitError("vertices", 2_000_000, 1_000_000),
        exceptions.Ms3dCapacityError("vertices", 513, 512),
        exceptions.ConversionError("conversion failed"),
        exceptions.AnimationError("animation failed"),
        exceptions.RegistryError("registry failed"),
        exceptions.RegionFileError("region"),
        exceptions.MergeInterrupted(),
    ),
)
def test_string(error: exceptions.ScFileException) -> None:
    assert str(error)
