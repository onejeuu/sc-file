import struct
from dataclasses import dataclass

from scfile.formats import FbxEncoder, McsbDecoder
from scfile.options import Options

from .conftest import ASSETS, export


type Property = bool | int | float | str | bytes | tuple[str, int]


@dataclass
class Node:
    name: str
    properties: list[Property]
    children: list["Node"]

    def child(self, name: str) -> "Node":
        return next(node for node in self.children if node.name == name)


def _nodes(data: bytes, offset: int = 27, end: int | None = None) -> list[Node]:
    nodes: list[Node] = []
    limit = len(data) if end is None else end - 13

    while offset < limit:
        node_end, count, _, name_size = struct.unpack_from("<IIIB", data, offset)
        if node_end == 0:
            break

        offset += 13
        name = data[offset : offset + name_size].decode()
        offset += name_size

        properties = []
        for _ in range(count):
            value, offset = _property(data, offset)
            properties.append(value)

        children = _nodes(data, offset, node_end) if offset < node_end else []
        nodes.append(Node(name, properties, children))
        offset = node_end

    return nodes


def _property(data: bytes, offset: int) -> tuple[Property, int]:
    tag = chr(data[offset])
    offset += 1
    scalars = {"C": "?", "Y": "h", "I": "i", "F": "f", "D": "d", "L": "q"}

    if tag in scalars:
        fmt = scalars[tag]
        return struct.unpack_from(f"<{fmt}", data, offset)[0], offset + struct.calcsize(fmt)

    if tag in {"S", "R"}:
        size, = struct.unpack_from("<I", data, offset)
        offset += 4
        value = data[offset : offset + size]
        return (value.decode() if tag == "S" else value), offset + size

    if tag in {"f", "d", "i", "l", "b"}:
        count, _, size = struct.unpack_from("<III", data, offset)
        return (tag, count), offset + 12 + size

    raise ValueError(f"Unknown FBX property type: {tag}")


def _array_type(node: Node) -> str:
    value = node.properties[0]
    assert isinstance(value, tuple)
    return value[0]


def test_structure() -> None:
    source = ASSETS / "models" / "source" / "model_v15.mcsb"
    roots = _nodes(export(McsbDecoder, FbxEncoder, source, Options()))
    nodes = {node.name: node for node in roots}

    definitions = nodes["Definitions"]
    assert definitions.child("Count").properties == [3]
    assert [(node.properties[0], node.child("Count").properties[0]) for node in definitions.children if node.name == "ObjectType"] == [
        ("Model", 1),
        ("Geometry", 1),
        ("Material", 1),
    ]

    geometry = nodes["Objects"].child("Geometry")
    layers = [node for node in geometry.children if node.name == "LayerElementUV"]
    assert [node.properties for node in layers] == [[0], [1]]
    assert [_array_type(node.child("UV")) for node in layers] == ["f", "f"]
    assert _array_type(geometry.child("Vertices")) == "f"
    assert _array_type(geometry.child("LayerElementNormal").child("Normals")) == "f"

    layer = geometry.child("Layer")
    elements = [node for node in layer.children if node.name == "LayerElement"]
    assert [(node.child("Type").properties[0], node.child("TypedIndex").properties[0]) for node in elements] == [
        ("Material", 0),
        ("UV", 0),
        ("UV", 1),
        ("Normal", 0),
    ]
