from scfile.consts import FileSignature
from scfile.core.base.decoder import FileDecoder
from scfile.core.data.model import ModelData
from scfile.core.formats.mcsa.parser import McsaParser
from scfile.enums import ByteOrder
from scfile.io.mcsa import McsaFileIO


class McsaDecoder(FileDecoder[McsaFileIO, ModelData, McsaParser]):
    order = ByteOrder.LITTLE
    signature = FileSignature.MCSA

    @property
    def opener(self):
        return McsaFileIO

    @property
    def file_data(self):
        return ModelData

    @property
    def file_parser(self):
        return McsaParser
