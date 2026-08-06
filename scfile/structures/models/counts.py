"""Counts declared by model formats."""

from dataclasses import dataclass


@dataclass
class ModelCounts:
    meshes: int = 0
    bones: int = 0
    channels: int = 0
    clips: int = 0


@dataclass
class MeshCounts:
    vertices: int = 0
    polygons: int = 0
    max_influences: int = 0
    local_bones: int = 0
    blend_shapes: int = 0
