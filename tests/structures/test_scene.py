from scfile.structures import models as S


def test_total_vertices():
    m1 = S.ModelMesh(count=S.MeshCounts(vertices=10))
    m2 = S.ModelMesh(count=S.MeshCounts(vertices=20))
    scene = S.ModelScene(meshes=[m1, m2])
    assert scene.total_vertices == 30


def test_total_vertices_empty():
    scene = S.ModelScene()
    assert scene.total_vertices == 0


def test_total_polygons():
    m1 = S.ModelMesh(count=S.MeshCounts(polygons=100))
    m2 = S.ModelMesh(count=S.MeshCounts(polygons=200))
    scene = S.ModelScene(meshes=[m1, m2])
    assert scene.total_polygons == 300


def test_total_polygons_empty():
    scene = S.ModelScene()
    assert scene.total_polygons == 0
