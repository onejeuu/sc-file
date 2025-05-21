from typing import NamedTuple


class Flags(NamedTuple):
    uv: bool
    normals: bool


TEMPLATE: dict[Flags, str] = {
    Flags(True, True): "f {a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}",
    Flags(True, False): "f {a}/{a} {b}/{b} {c}/{c}",
    Flags(False, True): "f {a}//{a} {b}//{b} {c}//{c}",
    Flags(False, False): "f {a} {b} {c}",
}
