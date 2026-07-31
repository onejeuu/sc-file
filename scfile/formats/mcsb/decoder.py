from typing import override

from scfile.enums import ByteOrder, F, FileFormat
from scfile.formats.mcsa.decoder import McsaDecoder


class McsbDecoder(McsaDecoder):
    format = FileFormat.MCSB

    @override
    def _prelude(self):
        self._skip_hash_prefix()

    def _skip_hash_prefix(self):
        size = self.io.value(F.I32, ByteOrder.BIG)
        self.io.read(size)
