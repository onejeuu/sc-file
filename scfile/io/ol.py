from scfile.consts import OlString
from scfile.io.binary import BinaryFileIO


class OlFileIO(BinaryFileIO):
    def readfourcc(self):
        """Read xor encoded FourCC."""
        # Read string and skip last 0x00 byte
        string = self.read(OlString.SIZE)[:-1]

        # Xor byte if it's is not null
        return bytes(byte ^ OlString.XOR for byte in string if byte != OlString.NULL)
