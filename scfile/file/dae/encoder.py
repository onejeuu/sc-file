import numpy as np
from collada import Collada, geometry, scene, source  # type: ignore

from scfile.file.data import ModelData

from .._base import FileEncoder


class DaeEncoder(FileEncoder[ModelData]):
    def serialize(self):
        self.model = self.data.model
        self.flags = self.data.model.flags

        self.model.ensure_unique_names()
        self.model.convert_polygons_to_global()

        self.collada = Collada()
        self.nodes: set[scene.Node] = set()

        # ? pycollada doesnt have skeleton support...

        for index, mesh in enumerate(self.model.meshes):
            # adding vertex positions source
            verts_id = f"{mesh.name}-verts-array"
            verts_data = np.array(
                [(v.position.x, v.position.y, v.position.z) for v in mesh.vertices]
            )
            verts = source.FloatSource(verts_id, verts_data, ("X", "Y", "Z"))

            # adding texture coodinates source
            texture_id = f"{mesh.name}-texture-array"
            texture_data = np.array(
                [(vertex.texture.u, -vertex.texture.v) for vertex in mesh.vertices]
            )
            texture = source.FloatSource(texture_id, texture_data, ("X", "Y"))

            # adding vertex normals source
            normals_id = f"{mesh.name}-normals-array"
            normals_data = np.array(
                [(v.normals.x, v.normals.y, v.normals.z) for v in mesh.vertices]
            )
            normals = source.FloatSource(normals_id, normals_data, ("X", "Y", "Z"))

            # adding geometry with sources
            geom = geometry.Geometry(
                self.collada, f"geometry-{index}", mesh.name, [verts, normals, texture]
            )

            input_list = source.InputList()
            input_list.addInput(0, "VERTEX", f"#{verts_id}")  # type: ignore
            input_list.addInput(0, "NORMAL", f"#{normals_id}")  # type: ignore
            input_list.addInput(0, "TEXCOORD", f"#{texture_id}")  # type: ignore

            # adding polygons
            indices = np.array([vertex_id for polygon in mesh.polygons for vertex_id in polygon])
            triset = geom.createTriangleSet(indices, input_list)  # type: ignore
            geom.primitives.append(triset)  # type: ignore
            self.collada.geometries.append(geom)

            # adding node
            geomnode = scene.GeometryNode(geom)
            node = scene.Node(mesh.name, children=[geomnode])
            self.nodes.add(node)

        # creating scene with nodes
        myscene = scene.Scene("scene", list(self.nodes))
        self.collada.scenes.append(myscene)
        self.collada.scene = myscene
        self.collada.write(self.buffer)  # type: ignore
