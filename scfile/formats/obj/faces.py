from typing import NamedTuple


type Template = bytes


class Flags(NamedTuple):
    uv: bool
    normals: bool


TEMPLATE: dict[Flags, Template] = {
    Flags(uv=True, normals=True): b"f %d/%d/%d %d/%d/%d %d/%d/%d\n",
    Flags(uv=True, normals=False): b"f %d/%d %d/%d %d/%d\n",
    Flags(uv=False, normals=True): b"f %d//%d %d//%d %d//%d\n",
    Flags(uv=False, normals=False): b"f %d %d %d\n",
}
