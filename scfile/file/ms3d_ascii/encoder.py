from scfile.file.data import ModelData
from scfile.file.encoder import FileEncoder
from scfile.utils.model import Mesh, Polygon

from scfile.enums import StructFormat as F

class Ms3dAsciiEncoder(FileEncoder[ModelData]):
    FLOAT_FORMAT = ".11f"
    
    def serialize(self):
        f = self.FLOAT_FORMAT
        self.model = self.data.model
        self.flags = self.data.model.flags

        self.offset = 0
        self.model.ensure_unique_names()
        
        self.b.writes(f"// MilkShape 3D ASCII\x0d\x0a\x0d\x0a")
        self.b.writes(f"Frames: 30\x0d\x0a")
        self.b.writes(f"Frame: 1\x0d\x0a\x0d\x0a")
        self.b.writes(f"Meshes: " + str(len(self.model.meshes)) + "\x0d\x0a")

        for m in self.model.meshes:
            i = self.model.meshes.index(m)
            self.b.writes(f"\"{i}_{m.name}\" 0 {i}\x0d\x0a")
            self.b.writes(f"{len(m.vertices)}\x0d\x0a")

            for v in m.vertices:
                id = -1
                weight = 0
                for key, value in v.bone.ids.items():
                    if v.bone.weights[key] > weight:
                        id = value
                        weight = v.bone.weights[key]
                
                self.b.writes(f"0 {v.position.x:{f}} {v.position.y:{f}} {v.position.z:{f}} {v.texture.u:{f}} {v.texture.v:{f}} {id}\x0d\x0a")

            self.b.writes(f"{len(m.vertices)}\x0d\x0a")
            for v in m.vertices:
                self.b.writes(f"{v.normals.x:{f}} {v.normals.y:{f}} {v.normals.z:{f}}\x0d\x0a")

            self.b.writes(f"{len(m.polygons)}\x0d\x0a")
            for p in m.polygons:
                self.b.writes(f"0 {p.a-1} {p.b-1} {p.c-1} {p.a-1} {p.b-1} {p.c-1} 1\x0d\x0a")

        self.b.writes(f"\x0d\x0aMaterials: {len(self.model.meshes)}\x0d\x0a")
        for m in self.model.meshes:
            i = self.model.meshes.index(m)
            self.b.writes(f"\"{i}_{m.material}\"\x0d\x0a")
            self.b.writes(f"0.200000 0.200000 0.200000 1.000000\x0d\x0a")
            self.b.writes(f"0.800000 0.800000 0.800000 1.000000\x0d\x0a")
            self.b.writes(f"0.000000 0.000000 0.000000 1.000000\x0d\x0a")
            self.b.writes(f"0.000000 0.000000 0.000000 1.000000\x0d\x0a")
            self.b.writes(f"0.000000\x0d\x0a")
            self.b.writes(f"1.000000\x0d\x0a")
            self.b.writes(f"\"\"\x0d\x0a")
            self.b.writes(f"\"\"\x0d\x0a")

        self.b.writes(f"\x0d\x0a") 

        if not self.model.skeleton:
            self.b.writes(f"Bones: 0\x0d\x0a") 
        else:
            self.b.writes(f"Bones: {len(self.model.skeleton.bones)}\x0d\x0a") 
            for b in self.model.skeleton.bones:
                self.b.writes(f"\"{b.name}\"\x0d\x0a") 
                if b.parent_id < 0:
                    self.b.writes(f"\"\"\x0d\x0a")
                else:
                    self.b.writes(f"\"{self.model.skeleton.bones[b.parent_id].name}\"\x0d\x0a") 
                self.b.writes(f"0 {b.position.x} {b.position.y} {b.position.z} {b.rotation.x} {b.rotation.y} {b.rotation.z}\x0d\x0a") 
                self.b.writes(f"0\x0d\x0a")
                self.b.writes(f"0\x0d\x0a")

        self.b.writes(f"GroupComments: 0\x0d\x0a") 
        self.b.writes(f"MaterialComments: 0\x0d\x0a") 
        self.b.writes(f"BoneComments: 0\x0d\x0a") 
        self.b.writes(f"ModelComment: 0\x0d\x0a") 

        