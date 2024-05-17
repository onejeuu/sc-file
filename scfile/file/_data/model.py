from dataclasses import dataclass

from scfile.utils.model import Model

from .base import FileData


@dataclass
class ModelData(FileData):
    model: Model
