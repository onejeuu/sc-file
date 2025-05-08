"""
Core module. It defines base classes and their interaction interface.
"""

from .decoder import FileDecoder
from .encoder import FileEncoder


__all__ = ("FileDecoder", "FileEncoder")
