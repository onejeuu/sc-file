from typing import override

from scfile.consts import FormatSignature
from scfile.core import Decoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.enums import SafetyLimit as Limit
from scfile.exceptions import BinaryStructureError
from scfile.io.models import ModelReader
from scfile.structures import models as S


class McalDecoder(Decoder[ModelContent, ModelReader]):
    format = FileFormat.MCAL
    signature = FormatSignature.MCAL
    order = ByteOrder.LITTLE

    content_type = ModelContent
    io_factory = ModelReader
    convertible = False

    @override
    def _parse(self):
        self._parse_header()
        self._parse_animation()
        if not self.io.eof():
            raise BinaryStructureError(location=self.location, offset=self.io.tell())

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

        bones = self.data.meta.counts.bones
        self.io.check(clip.frames * bones, Limit.TRANSFORMS)
        rotations, translations, _ = self.io.clip(
            clip.frames,
            bones,
            0,
            self.data.scene.scale.position,
        )
        clip.rotations = rotations
        clip.translations = translations

        # ? Version 14 clip metadata
        if self.data.meta.version >= 14.0:
            self.io.skip(2)

        self.data.scene.animation.clips.append(clip)
