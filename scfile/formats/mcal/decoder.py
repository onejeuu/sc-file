from scfile.consts import FileSignature
from scfile.core import FileDecoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.enums import SafetyLimit as Limit
from scfile.exceptions import InvalidStructureError
from scfile.formats.mcsa.io import McsaFileIO
from scfile.structures import models as S


class McalDecoder(FileDecoder[ModelContent], McsaFileIO):
    format = FileFormat.MCAL
    signature = FileSignature.MCAL
    order = ByteOrder.LITTLE

    content_factory = ModelContent
    convertible = False

    def parse(self):
        self._parse_header()
        self._parse_animation()
        if not self.is_eof():
            raise InvalidStructureError(self.location, self.tell())

    def _parse_header(self):
        self.data.version = self._readb(F.F32)
        self.ctx["COUNT_BONES"] = self._readb(F.U8)
        self.data.scene.scale.position = self._readb(F.F32)

    def _parse_animation(self):
        self.ctx["COUNT_CLIPS"] = self._readcount(F.I32, Limit.CLIPS)

        for _ in range(self.ctx["COUNT_CLIPS"]):
            self._parse_clip()

    def _parse_clip(self):
        clip = S.AnimationClip()

        clip.name = self._readutf8()
        clip.frames = self._readcount(F.U32, Limit.FRAMES)
        clip.rate = self._readb(F.F32)

        self._checklimit(clip.frames * self.ctx["COUNT_BONES"], Limit.TRANSFORMS)
        rotations, translations, _ = self._readclip(
            clip.frames,
            self.ctx["COUNT_BONES"],
            0,
            self.data.scene.scale.position,
        )
        clip.rotations = rotations
        clip.translations = translations

        # ? Version 14 clip metadata
        if self.data.version >= 14.0:
            self.skip(2)

        self.data.scene.animation.clips.append(clip)
