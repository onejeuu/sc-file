from scfile.core.base.encoder import FileEncoder
from scfile.core.data.model import ModelData
from scfile.enums import FileFormat

from .serializer import ObjSerializer


class ObjEncoder(FileEncoder[ModelData]):
    @property
    def format(self):
        return FileFormat.OBJ

    @property
    def file_serializer(self):
        return ObjSerializer

    def prepare(self):
        self.data.model.ensure_unique_names()
        self.data.model.convert_polygons_to_global(start_index=1)
