from typing import Literal, NamedTuple


Skip = Literal["-"]


class Model(NamedTuple):
    path: str
    filesize: int
    version: float
    meshes: int
    vertices: int
    polygons: int
    bones: int | Skip
    clips: int | Skip
    frames: int | Skip
    skeleton: bool
    uv: bool
    uv2: bool
    normals: bool
    tangents: bool
    colors: bool
    scale: float
    scale_uv: float
    scale_uv2: float


class Mesh(NamedTuple):
    path: str
    idx: int
    name: str
    material: str
    vertices: int
    polygons: int
    quads: bool
    max_influences: int | Skip


class Bone(NamedTuple):
    path: str
    idx: int
    name: str
    parent_idx: int


class Animation(NamedTuple):
    path: str
    idx: int
    name: str
    frames: int
    rate: float


class Texture(NamedTuple):
    path: str
    filesize: int
    fourcc: str
    width: int
    height: int
    kind: str
    mipmaps: int
    faces: int
    path_hash: str


class Image(NamedTuple):
    path: str
    filesize: int


class Arms(NamedTuple):
    animation: str
    model: str
    clips: int
    frames: int
    bones: int
    meshes: int
    vertices: int
    polygons: int


class Face(NamedTuple):
    animation: str
    model: str
    clips: int
    frames: int
    channels: int
    shapes: int
    mapped: int
    meshes: int
    vertices: int
    polygons: int


class Body(NamedTuple):
    animation: str
    model: str
    clips: int
    frames: int
    bones: int
    meshes: int
    vertices: int
    polygons: int


type Record = Model | Mesh | Bone | Animation | Texture | Image | Arms | Face | Body
