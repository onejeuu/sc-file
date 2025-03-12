from scfile.enums import ByteOrder
from scfile.enums import StructFormat as F
from scfile.formats.mcsa.decoder import McsaDecoder


class McsbDecoder(McsaDecoder):
    def prepare(self):
        self.read_hash_prefix()

    def read_hash_prefix(self):
        size = self.readb(F.I32, ByteOrder.BIG)
        self.read(size)
