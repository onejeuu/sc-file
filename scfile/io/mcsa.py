from scfile.consts import McsaModel
from scfile.enums import StructFormat as F
from scfile.exceptions.mcsa import McsaCountsLimit
from scfile.io.binary import BinaryFileIO


class McsaFileIO(BinaryFileIO):
    def readvalues(self, fmt: str, size: int, count: int):
        """Read repetitive data values."""
        return self.unpack(f"{size*count}{fmt}")

    def readcounts(self):
        """Read u32 value and validates count limit."""
        counts = self.readb(F.U32)
        if counts > McsaModel.COUNT_LIMIT:
            raise McsaCountsLimit(self.path, counts)
        return counts
