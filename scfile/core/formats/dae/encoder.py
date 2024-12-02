from scfile.core.base.encoder import FileEncoder
from scfile.core.data.model import ModelData
from scfile.enums import FileFormat

from .serializer import DaeSerializer


class DaeEncoder(FileEncoder[ModelData]):
    @property
    def format(self):
        return FileFormat.DAE

    @property
    def file_serializer(self):
        return DaeSerializer

    def prepare(self):
        self.data.model.ensure_unique_names()
        self.data.model.skeleton.convert_to_local()
        self.data.model.skeleton.build_hierarchy()
