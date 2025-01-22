from .enums import PrimitiveMode


VERSION = 2

BASE_GLTF = {
    "asset": {"version": "2.0", "generator": "onejeuu@scfile"},
    "scene": 0,
    "scenes": [],
    "nodes": [],
    "meshes": [],
    "skins": [],
    "accessors": [],
    "bufferViews": [],
    "buffers": [],
}

BASE_SCENE = {"name": "Scene", "nodes": []}
BASE_BUFFER = {"byteLength": 0}
BASE_PRIMITIVE = {"attributes": {}, "mode": PrimitiveMode.TRIANGLES}
