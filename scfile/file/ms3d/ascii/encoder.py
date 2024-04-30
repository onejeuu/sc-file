from scfile.consts import McsaModel
from scfile.file.data import ModelData
from scfile.file.encoder import FileEncoder
from scfile.utils.model import Mesh, Vertex


class Ms3dAsciiEncoder(FileEncoder[ModelData]):
    FLOAT_FORMAT = ".11f"
    SEPARATOR = "\x0d\x0a"

    def serialize(self):
        self.model = self.data.model
        self.meshes = self.data.model.meshes
        self.skeleton = self.model.skeleton
        self.flags = self.data.model.flags

        self.offset = 0
        self.model.ensure_unique_names()

        self._add_header()
        self._add_meshes()
        self._add_materials()
        self._add_skeleton()
        self._add_stats()

    def _add_header(self):
        s = self.SEPARATOR
        self.b.writes(f"// MilkShape 3D ASCII{s}{s}")
        self.b.writes(f"Frames: 30{s}")
        self.b.writes(f"Frame: 1{s}{s}")
        self.b.writes(f"Meshes: {len(self.meshes)}{s}")

    def _add_meshes(self):
        s = self.SEPARATOR

        for index, mesh in enumerate(self.meshes):
            self.b.writes(f'"{index}_{mesh.name}" 0 {index}{s}')
            self._add_vertices(mesh)
            self._add_normals(mesh)
            self._add_polygons(mesh)
        self.b.writes(s)

    def _get_bone_id(self, v: Vertex) -> int:
        bone_id = McsaModel.ROOT_BONE_ID
        weight = 0
        for key, value in v.bone.ids.items():
            if v.bone.weights[key] > weight:
                bone_id = value
                weight = v.bone.weights[key]
        return bone_id

    def _add_vertices(self, mesh: Mesh):
        f = self.FLOAT_FORMAT
        s = self.SEPARATOR

        self.b.writes(f"{len(mesh.vertices)}{s}")

        for v in mesh.vertices:
            bone_id = self._get_bone_id(v)

            self.b.writes(
                f"0 {v.position.x:{f}} {v.position.y:{f}} {v.position.z:{f}} {v.texture.u:{f}} {v.texture.v:{f}} {bone_id}{s}"
            )

    def _add_normals(self, mesh: Mesh):
        f = self.FLOAT_FORMAT
        s = self.SEPARATOR

        self.b.writes(f"{len(mesh.vertices)}{s}")

        for v in mesh.vertices:
            self.b.writes(f"{v.normals.x:{f}} {v.normals.y:{f}} {v.normals.z:{f}}{s}")

    def _add_polygons(self, mesh: Mesh):
        s = self.SEPARATOR

        self.b.writes(f"{len(mesh.polygons)}{s}")

        for p in mesh.polygons:
            self.b.writes(f"0 {p.a} {p.b} {p.c} {p.a} {p.b} {p.c} 1{s}")

    def _add_materials(self):
        s = self.SEPARATOR

        self.b.writes(f"Materials: {len(self.model.meshes)}{s}")

        for index, mesh in enumerate(self.model.meshes):
            self.b.writes(f'"{index}_{mesh.material}"{s}')
            self.b.writes(f"0.200000 0.200000 0.200000 1.000000{s}")
            self.b.writes(f"0.800000 0.800000 0.800000 1.000000{s}")
            self.b.writes(f"0.000000 0.000000 0.000000 1.000000{s}")
            self.b.writes(f"0.000000 0.000000 0.000000 1.000000{s}")
            self.b.writes(f"0.000000{s}")
            self.b.writes(f"1.000000{s}")
            self.b.writes(f'""{s}')
            self.b.writes(f'""{s}')
        self.b.writes(s)

    def _add_skeleton(self):
        f = self.FLOAT_FORMAT
        s = self.SEPARATOR

        if not self.flags.skeleton:
            self.b.writes(f"Bones: 0{s}")
            return

        self.b.writes(f"Bones: {len(self.skeleton.bones)}{s}")

        for b in self.skeleton.bones:
            self.b.writes(f'"{b.name}"{s}')

            if b.parent_id < 0:
                self.b.writes(f'""{s}')
            else:
                parent_name = self.skeleton.bones[b.parent_id].name
                self.b.writes(f'"{parent_name}"{s}')

            self.b.writes(
                f"0 {b.position.x:{f}} {b.position.y:{f}} {b.position.z:{f}} {b.rotation.x:{f}} {b.rotation.y:{f}} {b.rotation.z:{f}}{s}"
            )
            self.b.writes(f"0{s}")
            self.b.writes(f"0{s}")

    def _add_stats(self):
        s = self.SEPARATOR
        self.b.writes(f"GroupComments: 0{s}")
        self.b.writes(f"MaterialComments: 0{s}")
        self.b.writes(f"BoneComments: 0{s}")
        self.b.writes(f"ModelComment: 0{s}")
