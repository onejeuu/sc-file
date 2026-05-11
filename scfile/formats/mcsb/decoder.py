from scfile.enums import ByteOrder, F, FileFormat
from scfile.formats.mcsa.decoder import McsaDecoder


class McsbDecoder(McsaDecoder):
    format = FileFormat.MCSB

    def prepare(self):
        self._skip_hash_prefix()

    def _skip_hash_prefix(self):
        size = self._readb(F.I32, ByteOrder.BIG)
        self.read(size)
