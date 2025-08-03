from typing import NamedTuple, TypeAlias


Template: TypeAlias = str


class Flags(NamedTuple):
    uv: bool
    normals: bool


TEMPLATE: dict[Flags, Template] = {
    Flags(uv=True, normals=True): "f {a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}",
    Flags(uv=True, normals=False): "f {a}/{a} {b}/{b} {c}/{c}",
    Flags(uv=False, normals=True): "f {a}//{a} {b}//{b} {c}//{c}",
    Flags(uv=False, normals=False): "f {a} {b} {c}",
}
