from scfile.consts import OlString
from scfile.io.binary import BinaryFileIO


class OlFileIO(BinaryFileIO):
    def readfourcc(self):
        # read string and skip last 0x00 byte
        string = self.read(OlString.SIZE)[:-1]

        # xor byte if it's is not null
        return bytes(byte ^ OlString.XOR for byte in string if byte != OlString.NULL)
