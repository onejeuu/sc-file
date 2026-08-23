from typing import override

from scfile.consts import FormatSignature
from scfile.content import models as S
from scfile.content.models import Feature
from scfile.core import ModelDecoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.enums import SafetyLimit as Limit
from scfile.io.models import ModelReader


class McalDecoder(ModelDecoder[ModelReader]):
    format = FileFormat.MCAL
    signature = FormatSignature.MCAL
    order = ByteOrder.LITTLE

    io_factory = ModelReader
    standalone = False
    features = (Feature.BONE_ANIMATION,)

    @override
    def _parse(self):
        self._parse_header()
        self._parse_animation()

    def _parse_header(self):
        self.data.meta.version = self.io.value(F.F32)
        self.data.meta.counts.bones = self.io.value(F.U8)
        self.data.scene.scale.position = self.io.value(F.F32)

    def _parse_animation(self):
        clips = self.io.count(F.I32, Limit.CLIPS)
        self.data.meta.counts.clips = clips

        for _ in range(clips):
            self._parse_clip()

    def _parse_clip(self):
        clip = S.AnimationClip()

        clip.name = self.io.string()
        clip.frames = self.io.count(F.U32, Limit.FRAMES)
        clip.rate = self.io.value(F.F32)

        channels = self.io.value(F.U16) if self.data.meta.version >= 14.0 else 0
        bones = self.data.meta.counts.bones
        self.io.check(clip.frames * bones, Limit.TRANSFORMS)
        self.io.check(clip.frames * channels, Limit.WEIGHTS)

        rotations, translations, morph_weights = self.io.clip(
            clip.frames,
            bones,
            channels,
            self.data.scene.scale.position,
        )
        clip.rotations = rotations
        clip.translations = translations
        clip.morph_weights = morph_weights

        self.data.scene.animation.clips.append(clip)
