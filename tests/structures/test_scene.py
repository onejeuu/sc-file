import numpy as np

from scfile.content.models import ModelMesh, ModelScene


def test_totals() -> None:
    scene = ModelScene(
        meshes=[
            ModelMesh(
                vertices=np.zeros((10, 3), dtype=np.float32),
                polygons=np.zeros((20, 3), dtype=np.uint32),
            ),
            ModelMesh(
                vertices=np.zeros((30, 3), dtype=np.float32),
                polygons=np.zeros((40, 3), dtype=np.uint32),
            ),
        ]
    )

    assert scene.total_vertices == 40
    assert scene.total_polygons == 60
