"""Handlers specialized for model content."""

from typing import ClassVar

from scfile.io.base import StructReader, StructWriter
from scfile.structures.models import Feature, Features

from .content import ModelContent
from .decoder import Decoder
from .encoder import Encoder


class ModelDecoder[
    ReaderType: StructReader = StructReader,
](Decoder[ModelContent, ReaderType]):
    """Base decoder for model formats."""

    content_type = ModelContent

    features: ClassVar[Features] = ()
    """Model features supported by the decoder."""

    @classmethod
    def supports(
        cls,
        feature: Feature,
    ) -> bool:
        """Return whether the decoder supports a model feature."""

        return any(member in cls.features for member in feature.members)


class ModelEncoder[
    WriterType: StructWriter = StructWriter,
](Encoder[ModelContent, WriterType]):
    """Base encoder for model formats."""

    content_type = ModelContent

    features: ClassVar[Features] = ()
    """Model features supported by the encoder."""

    @classmethod
    def supports(
        cls,
        feature: Feature,
    ) -> bool:
        """Return whether the encoder supports a model feature."""

        return any(member in cls.features for member in feature.members)

    def includes(
        self,
        feature: Feature,
    ) -> bool:
        """Return whether a model feature will be serialized."""

        if feature.parent is Feature.ANIMATION and not self.options.animation:
            return False

        if feature is Feature.SKELETON and not self.options.skeleton_enabled:
            return False

        return any(
            self.data.has(member)
            and self.supports(member)
            and all(self.includes(required) for required in member.requires)
            for member in feature.members
        )
