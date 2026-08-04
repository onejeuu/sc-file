"""
File formats registry.
"""

from .default import REGISTRY, RESOLVER
from .registry import FormatSpec, Registry
from .resolver import Resolver


__all__ = (
    "REGISTRY",
    "RESOLVER",
    "FormatSpec",
    "Registry",
    "Resolver",
)
