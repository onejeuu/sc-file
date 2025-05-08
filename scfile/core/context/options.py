"""
Shared user options between decoder and encoder.
"""

from abc import ABC
from dataclasses import dataclass


@dataclass
class FileOptions(ABC):
    pass


@dataclass
class ModelOptions(FileOptions):
    parse_skeleton: bool = False
    parse_animation: bool = False
    calculate_tangents: bool = False


# TODO
@dataclass
class AnimationOptions(FileOptions):
    pass


@dataclass
class TextureOptions(FileOptions):
    is_hdri: bool = False


@dataclass
class ImageOptions(FileOptions):
    pass
