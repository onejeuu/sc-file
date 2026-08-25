"""Model handler specializations."""

from typing import ClassVar

from scfile.content import ModelContent
from scfile.content.models import Feature, Features
from scfile.io.base import StructReader, StructWriter

from .decoder import Decoder
from .encoder import Encoder


class ModelDecoder[
    ReaderType: StructReader = StructReader,
](Decoder[ModelContent, ReaderType]):
    """Decoder base class for model content."""

    content_type = ModelContent

    features: ClassVar[Features] = ()
    """Features supported by this decoder."""

    @classmethod
    def supports(
        cls,
        feature: Feature,
    ) -> bool:
        """Return whether this decoder supports a feature."""

        return any(member in cls.features for member in feature.members)


class ModelEncoder[
    WriterType: StructWriter = StructWriter,
](Encoder[ModelContent, WriterType]):
    """Encoder base class for model content."""

    content_type = ModelContent

    features: ClassVar[Features] = ()
    """Features supported by this encoder."""

    @classmethod
    def supports(
        cls,
        feature: Feature,
    ) -> bool:
        """Return whether this encoder supports a feature."""

        return any(member in cls.features for member in feature.members)

    def includes(
        self,
        feature: Feature,
    ) -> bool:
        """Return whether a feature will be serialized."""

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
