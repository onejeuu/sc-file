"""Handler-controlled requirements and Core-owned resource resolution."""

from inspect import Parameter, signature

import pytest

from scfile.content import BaseContent
from scfile.core import Decoder, Encoder, Resources
from scfile.enums import HandlerState
from scfile.exceptions import EmptyFileError
from scfile.options import Options


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

    assert signature(DecoderWithRequirements.__mro__[1]).parameters["resources"].kind is Parameter.POSITIONAL_OR_KEYWORD
    assert signature(EncoderWithRequirements.__mro__[1]).parameters["resources"].kind is Parameter.POSITIONAL_OR_KEYWORD
