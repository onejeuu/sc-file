import numpy as np

from scfile.structures import models as S


def test_total_vertices():
    m1 = S.ModelMesh(vertices=np.zeros((10, 3), dtype=np.float32))
    m2 = S.ModelMesh(vertices=np.zeros((20, 3), dtype=np.float32))
    scene = S.ModelScene(meshes=[m1, m2])
    assert scene.total_vertices == 30


def test_total_vertices_empty():
    scene = S.ModelScene()
    assert scene.total_vertices == 0


def test_total_polygons():
    m1 = S.ModelMesh(polygons=np.zeros((100, 3), dtype=np.uint32))
    m2 = S.ModelMesh(polygons=np.zeros((200, 3), dtype=np.uint32))
    scene = S.ModelScene(meshes=[m1, m2])
    assert scene.total_polygons == 300


def test_total_polygons_empty():
    scene = S.ModelScene()
    assert scene.total_polygons == 0
