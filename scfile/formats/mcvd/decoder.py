from scfile.enums import FileFormat
from scfile.formats.mcsa.decoder import McsaDecoder


class McvdDecoder(McsaDecoder):
    format = FileFormat.MCVD
