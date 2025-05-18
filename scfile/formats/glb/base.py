from .enums import PrimitiveMode


GLTF = {
    "asset": {"version": "2.0", "generator": "onejeuu@scfile"},
    "scene": 0,
    "scenes": [],
    "nodes": [],
    "materials": [],
    "meshes": [],
    "accessors": [],
    "bufferViews": [],
    "buffers": [],
}

SCENE = {"name": "Scene", "nodes": []}

BUFFER = {"byteLength": 0}

PRIMITIVE = {"attributes": {}, "mode": PrimitiveMode.TRIANGLES.value}

# R, G, B, A
COLOR = [0.5, 0.5, 0.5, 1.0]

# pbrMetallicRoughness
PBR = {"baseColorFactor": COLOR}
