import pytest

from scfile import exceptions
from scfile.core import DocumentContent, ModelDecoder, ModelEncoder
from scfile.enums import FileFormat
from scfile.options import Options
from scfile.registry import Registry, Resolver
from scfile.structures.models import Feature

from tests.conftest import BytesDecoder, BytesEncoder


class RegistryDecoder(BytesDecoder):
    format = FileFormat.MIC


class RegistryEncoder(BytesEncoder):
    format = FileFormat.PNG


class DdsEncoder(BytesEncoder):
    format = FileFormat.DDS


class OtherDecoder(BytesDecoder):
    format = FileFormat.MIC


class DocumentEncoder(RegistryEncoder):
    format = FileFormat.MIC
    content_type = DocumentContent


class RegistryModelDecoder(ModelDecoder):
    format = FileFormat.MCSA

    def _parse(self) -> None:
        pass


class RelatedDecoder(RegistryDecoder):
    format = FileFormat.MCAL
    standalone = False


class RegistryObjEncoder(ModelEncoder):
    format = FileFormat.OBJ

    def _serialize(self) -> None:
        pass


class RegistryGlbEncoder(ModelEncoder):
    format = FileFormat.GLB
    features = (Feature.SKELETON,)

    def _serialize(self) -> None:
        pass


def test_target() -> None:
    registry = Registry(RegistryDecoder, RegistryEncoder)
    registry.alias(FileFormat.MIC, "thumbnail")

    assert registry.resolve(".mic") is FileFormat.MIC
    assert registry.resolve("thumbnail") is FileFormat.MIC
    assert registry.targets(FileFormat.MIC) == {FileFormat.PNG: RegistryEncoder}


def test_alias() -> None:
    registry = Registry(RegistryDecoder, RegistryEncoder)
    registry.alias(FileFormat.MIC, "thumbnail")

    assert Resolver(registry).resolve("assets/thumbnail") is registry.get(FileFormat.MIC)


def test_inputs() -> None:
    registry = Registry(RegistryDecoder)
    registry.alias(FileFormat.MIC, "thumbnail")

    assert registry.supported_formats == {FileFormat.MIC}
    assert registry.supported_suffixes == {".mic"}
    assert registry.supported_aliases == {"thumbnail"}
    assert registry.supported_inputs == {".mic", "thumbnail"}
    assert registry.filters_for(FileFormat.MIC) == {".mic", "thumbnail"}


def test_unknown() -> None:
    registry = Registry()

    with pytest.raises(exceptions.RegistryError):
        registry.resolve("unknown")
    with pytest.raises(exceptions.RegistryError):
        registry.alias(FileFormat.MIC, "thumbnail")

    assert registry.get("unknown") is None


def test_copy() -> None:
    registry = Registry(RegistryDecoder, RegistryEncoder)
    copied = registry.copy()
    copied.alias(FileFormat.MIC, "thumbnail")

    assert "thumbnail" not in registry.aliases
    assert copied.resolve("thumbnail") is FileFormat.MIC


def test_duplicate() -> None:
    registry = Registry(RegistryDecoder)

    with pytest.raises(exceptions.RegistryError):
        registry.register(OtherDecoder)


def test_content() -> None:
    registry = Registry(RegistryDecoder)

    with pytest.raises(exceptions.RegistryError):
        registry.register(DocumentEncoder)


def test_model_targets() -> None:
    registry = Registry(RegistryModelDecoder, RegistryObjEncoder, RegistryGlbEncoder)

    assert registry.target(FileFormat.MCSA) is RegistryObjEncoder
    assert registry.target(FileFormat.MCSA, Options(model={"skeleton": True})) is RegistryGlbEncoder


def test_model_supports() -> None:
    registry = Registry(RegistryObjEncoder, RegistryGlbEncoder)

    assert registry.model_supports(FileFormat.GLB, Feature.SKELETON)
    assert not registry.model_supports(FileFormat.OBJ, Feature.SKELETON)
    assert not registry.model_supports(FileFormat.MIC, Feature.SKELETON)


def test_non_model_target() -> None:
    registry = Registry(RegistryDecoder, RegistryEncoder)

    assert registry.target(FileFormat.MIC) is RegistryEncoder


def test_ambiguous_target() -> None:
    registry = Registry(RegistryDecoder, RegistryEncoder, DdsEncoder)

    assert registry.target(FileFormat.MIC) is None


def test_related_source() -> None:
    registry = Registry(RelatedDecoder, RegistryEncoder)

    assert registry.targets(FileFormat.MCAL) == {}


def test_output_only() -> None:
    resolver = Resolver(Registry(RegistryEncoder))

    assert resolver.resolve("image.png") is None
