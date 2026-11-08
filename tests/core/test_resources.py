from scfile.enums import HandlerState
from scfile.exceptions import EmptyFileError
from scfile.options import Options

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


class Content(BaseContent):
    pass


class EncoderWithRequirements(Encoder[Content]):
    content_type = Content
    events: list[str]

    def __init__(self, *args, **kwargs):
        self.events = []
        super().__init__(*args, **kwargs)

    def _requirements(self):
        return {"prepared": self._make_resource}

    def _make_resource(self):
        self.events.append("factory")
        return object()

    def _prelude(self):
        assert "prepared" in self.resources
        self.events.append("prelude")

    def _serialize(self):
        self.events.append("serialize")
        self.io.write(b"ok")


class DecoderWithRequirements(Decoder[Content]):
    content_type = Content
    events: list[str]

    def __init__(self, *args, **kwargs):
        self.events = []
        super().__init__(*args, **kwargs)

    def _verify_filesize(self):
        self.events.append("filesize")
        super()._verify_filesize()

    def _requirements(self):
        return {"prepared": self._make_resource}

    def _make_resource(self):
        self.events.append("factory")
        return object()

    def _prelude(self):
        assert "prepared" in self.resources
        self.events.append("prelude")

    def _parse(self):
        self.events.append("parse")


def test_resource_resolution_is_deferred_and_precedes_encoder_prelude():
    with EncoderWithRequirements(Content()) as encoder:
        assert encoder.events == []
        assert encoder.resources == {}
        assert encoder.to_bytes() == b"ok"
        assert encoder.events == ["factory", "prelude", "serialize"]
        assert encoder.to_bytes() == b"ok"
        assert encoder.events == ["factory", "prelude", "serialize"]


def test_prepared_resources_are_reused_without_factory_or_copy():
    prepared = object()
    resources = Resources({"prepared": prepared})

    with EncoderWithRequirements(Content(), resources=resources) as encoder:
        assert encoder.to_bytes() == b"ok"
        assert encoder.events == ["prelude", "serialize"]
        assert encoder.resources is resources
        assert encoder.resources["prepared"] is prepared


def test_missing_resources_create_a_derived_container_without_mutation():
    other = object()
    resources = Resources({"other": other})

    with EncoderWithRequirements(Content(), resources=resources) as encoder:
        encoder.encode()
        assert encoder.resources is not resources
        assert encoder.resources["other"] is other
        assert "prepared" in encoder.resources
        assert list(resources) == ["other"]
        with pytest.raises(TypeError):
            encoder.resources["invalid"] = None  # type: ignore[index]


def test_decoder_validates_file_size_before_resource_resolution_and_prelude():
    with DecoderWithRequirements(b"input") as decoder:
        decoder.decode()
        assert decoder.events == ["filesize", "factory", "prelude", "parse"]
        decoder.decode()
        assert decoder.events == ["filesize", "factory", "prelude", "parse"]

    with DecoderWithRequirements(b"") as decoder:
        with pytest.raises(EmptyFileError):
            decoder.decode()
        assert decoder.events == ["filesize"]
        assert decoder.state is HandlerState.FAILED


def test_decoder_propagates_its_resolved_resources_to_convert_to():
    with DecoderWithRequirements(b"input") as decoder:
        with decoder.convert_to(EncoderWithRequirements) as encoder:
            assert encoder.resources is decoder.resources
            assert encoder.resources["prepared"] is decoder.resources["prepared"]
            assert encoder.to_bytes() == b"ok"
            assert encoder.resources is decoder.resources


def test_handler_can_override_the_resolution_algorithm():
    class RequiredEncoder(EncoderWithRequirements):
        def _resolve_resources(self):
            if "prepared" not in self.resources:
                raise RuntimeError("resource must be provided")

    with RequiredEncoder(Content()) as encoder:
        with pytest.raises(RuntimeError, match="resource must be provided"):
            encoder.encode()
        assert encoder.events == []

    with RequiredEncoder(Content(), resources=Resources({"prepared": object()})) as encoder:
        assert encoder.to_bytes() == b"ok"
        assert encoder.events == ["prelude", "serialize"]


def test_positional_resources_on_handler_constructors():
    resource = Resources({"prepared": object()})
    options = Options()
    with DecoderWithRequirements(b"input", options, resource) as decoder:
        assert decoder.resources is resource
        decoder.decode()
        assert decoder.resources is resource

    with EncoderWithRequirements(Content(), options, None, resource) as encoder:
        assert encoder.resources is resource
        assert encoder.to_bytes() == b"ok"
