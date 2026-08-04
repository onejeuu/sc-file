from typing import override

from scfile.consts import FileSignature
from scfile.core import Decoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.enums import SafetyLimit as Limit
from scfile.exceptions import BinaryStructureError
from scfile.io.models import ModelReader
from scfile.structures import models as S


class McalDecoder(Decoder[ModelContent, ModelReader]):
    format = FileFormat.MCAL
    signature = FileSignature.MCAL
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
        self.data.version = self.io.value(F.F32)
        self._ctx["COUNT_BONES"] = self.io.value(F.U8)
        self.data.scene.scale.position = self.io.value(F.F32)

    def _parse_animation(self):
        self._ctx["COUNT_CLIPS"] = self.io.count(F.I32, Limit.CLIPS)

        for _ in range(self._ctx["COUNT_CLIPS"]):
            self._parse_clip()

    def _parse_clip(self):
        clip = S.AnimationClip()

        clip.name = self.io.string()
        clip.frames = self.io.count(F.U32, Limit.FRAMES)
        clip.rate = self.io.value(F.F32)

        self.io.check(clip.frames * self._ctx["COUNT_BONES"], Limit.TRANSFORMS)
        rotations, translations, _ = self.io.clip(
            clip.frames,
            self._ctx["COUNT_BONES"],
            0,
            self.data.scene.scale.position,
        )
        clip.rotations = rotations
        clip.translations = translations

        # ? Version 14 clip metadata
        if self.data.version >= 14.0:
            self.io.skip(2)

        self.data.scene.animation.clips.append(clip)
