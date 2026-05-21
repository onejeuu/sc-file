from scfile.consts import FileSignature
from scfile.core import FileDecoder, ModelContent
from scfile.enums import ByteOrder, F, FileFormat
from scfile.formats.mcsa.io import McsaFileIO
from scfile.structures import models as S


class McalDecoder(FileDecoder[ModelContent], McsaFileIO):
    format = FileFormat.MCAL
    signature = FileSignature.MCAL
    order = ByteOrder.LITTLE

    _content = ModelContent

    def parse(self):
        self._parse_header()
        self._parse_animation()

    def _parse_header(self):
        self.data.version = self._readb(F.F32)
        self.ctx["COUNT_BONES"] = self._readb(F.U32)
        self.ctx["UNKNOWN_SIZE"] = self._readb(F.U8)

    def _parse_animation(self):
        self.ctx["COUNT_CLIPS"] = self._readb(F.I32)

        for _ in range(self.ctx["COUNT_CLIPS"]):
            self._parse_clip()

    def _parse_clip(self):
        clip = S.AnimationClip()

        clip.name = self._readutf8()
        clip.frames = self._readb(F.U32)
        clip.rate = self._readb(F.F32)

        rotations, translations = self._readclip(clip.frames, self.ctx["COUNT_BONES"])
        clip.rotations = rotations
        clip.translations = translations

        self.data.scene.animation.clips.append(clip)
