from scfile.core.base.encoder import FileEncoder
from scfile.core.data.model import ModelData
from scfile.enums import FileFormat

from .serializer import GlbSerializer


class GlbEncoder(FileEncoder[ModelData]):
    @property
    def format(self):
        return FileFormat.GLB

    @property
    def file_serializer(self):
        return GlbSerializer

    def prepare(self):
        self.data.model.ensure_unique_names()
        self.data.model.skeleton.convert_to_local()
        self.data.model.skeleton.build_hierarchy()
