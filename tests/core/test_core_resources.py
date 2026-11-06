from inspect import Parameter, signature

import pytest

from scfile.content import BaseContent
from scfile.core import Decoder, Encoder, Resources


class DummyContent(BaseContent):
    pass


class DummyDecoder(Decoder[DummyContent]):
    content_type = DummyContent

    def _parse(self) -> None:
        pass


class DummyEncoder(Encoder[DummyContent]):
    content_type = DummyContent

    def _serialize(self) -> None:
        self.io.write(b"encoded")


def test_resources_exposes_read_only_mapping() -> None:
    value = object()
    source = {"example": value}
    resources = Resources(source)

    source["example"] = object()

    assert resources["example"] is value
    assert dict(resources) == {"example": value}
    with pytest.raises(TypeError):
        resources["other"] = object()  # type: ignore[index]


def test_handlers_keep_the_supplied_resources_instance() -> None:
    resources = Resources({"example": object()})
    decoder = DummyDecoder(b"source", resources=resources)
    encoder = DummyEncoder(DummyContent(), resources=resources)

    try:
        assert decoder.resources is resources
        assert encoder.resources is resources
        assert decoder.context == {}
        assert decoder.context is not decoder.resources
    finally:
        decoder.close()
        encoder.close()


def test_handlers_get_independent_empty_resources_by_default() -> None:
    first = DummyDecoder(b"first")
    second = DummyDecoder(b"second")

    try:
        assert isinstance(first.resources, Resources)
        assert isinstance(second.resources, Resources)
        assert first.resources == second.resources == {}
        assert first.resources is not second.resources
    finally:
        first.close()
        second.close()


def test_decoder_convert_to_reuses_its_resources() -> None:
    resources = Resources({"example": object()})

    with DummyDecoder(b"source", resources=resources) as decoder:
        with decoder.convert_to(DummyEncoder) as encoder:
            assert encoder.resources is resources
            assert encoder.to_bytes() == b"encoded"


def test_decoder_convert_reuses_its_resources() -> None:
    resources = Resources({"example": object()})

    with DummyDecoder(b"source", resources=resources) as decoder:
        assert decoder.convert(DummyEncoder) == b"encoded"


def test_resources_is_positional_on_handler_constructors() -> None:
    decoder_parameters = signature(DummyDecoder).parameters
    encoder_parameters = signature(DummyEncoder).parameters

    assert tuple(decoder_parameters) == ("stream", "options", "resources")
    assert decoder_parameters["resources"].kind is Parameter.POSITIONAL_OR_KEYWORD
    assert tuple(encoder_parameters) == ("data", "options", "output", "resources")
    assert encoder_parameters["resources"].kind is Parameter.POSITIONAL_OR_KEYWORD
