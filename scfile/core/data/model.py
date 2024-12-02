from collections import defaultdict

from scfile.core.data.base import FileData
from scfile.utils.model.scene import ModelScene


class ModelData(FileData):
    version: float = 0.0
    flags: defaultdict[int, bool] = defaultdict(bool)
    model: ModelScene = ModelScene()
