import struct
from typing import override

from scfile.consts import FormatSignature
from scfile.content import DocumentContent
from scfile.core import Decoder
from scfile.enums import ByteOrder, F, FileFormat


class SignDecoder(Decoder[DocumentContent]):
    format = FileFormat.SIGN
    signature = FormatSignature.SIGN
    order = ByteOrder.BIG

    content_type = DocumentContent

    exportable = False

    @override
    def _prelude(self):
        self._ctx["hash"] = self.io.prefixed(F.U32)

    @override
    def _parse(self):
        self.data.value = {
            "hash": self._ctx["hash"],
            "version": self.io.value(F.U32),
            "textures": [self._parse_texture() for _ in range(self.io.value(F.U32))],
        }

    def _parse_texture(self):
        path = self.io.string()
        height, width, mipmap_count, face_count = self.io.unpack("4I")
        return {
            "path": path,
            "height": height,
            "width": width,
            "mipmap_count": mipmap_count,
            "face_count": face_count,
            "format": self.io.string(),
            "mipmaps": self._parse_mipmaps(),
        }

    def _parse_mipmaps(self):
        count = self.io.value(F.U32)
        fmt = f"{self.order}4I32s"
        data = self.io.read_exact(count * struct.calcsize(fmt))
        return [
            {
                "index": index,
                "cube_face": cube_face,
                "compressed_size": compressed_size,
                "uncompressed_size": uncompressed_size,
                "sha256": sha256,
            }
            for index, cube_face, compressed_size, uncompressed_size, sha256 in struct.iter_unpack(fmt, data)
        ]
