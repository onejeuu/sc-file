from typing import override

from scfile.enums import ByteOrder, F, FileFormat
from scfile.formats.mcsa.decoder import McsaDecoder


class McsbDecoder(McsaDecoder):
    format = FileFormat.MCSB

    @override
    def _prelude(self):
        self._skip_hash_prefix()

    def _skip_hash_prefix(self):
        offset = self.io.tell()
        size = self.io.value(F.I32, ByteOrder.BIG)

        if size < 0 or size > self.io.size() - offset - 4:
            self.io.seek(offset)
            return

        if size > 0:
            self.io.read(size)
