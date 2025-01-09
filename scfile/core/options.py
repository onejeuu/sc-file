from abc import ABC
from dataclasses import dataclass


# these are more only decoder options
# not sure what options will be for encoders
# but lets use generic name
@dataclass
class FileOptions(ABC):
    pass


# ? Test Examples
@dataclass
class ModelOptions(FileOptions):
    parse_skeleton: bool = True
    parse_animations: bool = True
    calculate_tangents: bool = False


@dataclass
class TextureOptions(FileOptions):
    is_cubemaps: bool = False
