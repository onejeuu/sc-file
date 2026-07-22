from typing import NamedTuple, TypeAlias


class Model(NamedTuple):
    path: str
    filesize: int
    version: float
    meshes: int
    vertices: int
    polygons: int
    bones: int
    clips: int
    frames: int
    skeleton: bool
    uv: bool
    uv2: bool
    normals: bool
    tangents: bool
    colors: bool
    scale: float
    scale_uv: float
    scale_uv2: float
    scale_filtering: float


class Mesh(NamedTuple):
    path: str
    idx: int
    name: str
    material: str
    vertices: int
    polygons: int
    quads: bool
    max_influences: int


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
    scformat: str
    fourcc: str
    width: int
    height: int
    kind: str
    mipmaps: int
    faces: int
    uncompressed_size: int
    compressed_size: int
    texture_id: str


class Image(NamedTuple):
    path: str
    filesize: int


Record: TypeAlias = Model | Mesh | Bone | Animation | Texture | Image
