from typing import override

from scfile.content import RegionContent
from scfile.core import Decoder
from scfile.enums import ByteOrder, FileFormat
from scfile.exceptions import DecodingError

from .v5.decoder import RegionDecoder as V5Decoder
from .v6.decoder import RegionDecoder as V6Decoder
from .v7.decoder import RegionDecoder as V7Decoder


SUPPORTED_VERSIONS = (5, 6, 7)
LATEST_VERSION = 7
DECODERS = {5: V5Decoder, 6: V6Decoder, 7: V7Decoder}


class MdatDecoder(Decoder[RegionContent]):
    format = FileFormat.MDAT
    order = ByteOrder.BIG

    content_type = RegionContent

    @override
    def _parse(self) -> None:
        version = self.options.mdat_version
        implementation = DECODERS.get(version)
        if implementation is None:
            raise DecodingError(f"Unsupported MDAT version: {version}.", location=self.location)
        self.data = implementation(self.io, self.options).read()
