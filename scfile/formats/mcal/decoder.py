from scfile.consts import FileSignature
from scfile.core.context.content import ModelContent
from scfile.core.decoder import FileDecoder
from scfile.enums import ByteOrder, F, FileFormat
from scfile.formats.mcsa.io import McsaFileIO
from scfile.structures import models as S


class McalDecoder(FileDecoder[ModelContent], McsaFileIO):
    format = FileFormat.MCAL
    order = ByteOrder.LITTLE
    signature = FileSignature.MCAL

    _content = ModelContent

    def parse(self):
        self._parse_header()
        self._parse_animation()

    def _parse_header(self):
        self.data.version = self._readb(F.F32)
        self.data.scene.count.bones = self._readb(F.U32)
        _ = self._readb(F.U8)  # ? some buffer size

    def _parse_animation(self):
        self.data.scene.count.clips = self._readb(F.I32)

        for _ in range(self.data.scene.count.clips):
            self._parse_clip()

    def _parse_clip(self):
        clip = S.AnimationClip()

        clip.name = self._readutf8()
        clip.frames = self._readb(F.U32)
        clip.rate = self._readb(F.F32)
        clip.transforms = self._readclip(clip.frames, self.data.scene.count.bones)

        self.data.scene.animation.clips.append(clip)
