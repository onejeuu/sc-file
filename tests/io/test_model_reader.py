import numpy as np

from scfile.consts import IntegerFactor as Factor
from scfile.enums import F
from scfile.io.models import ModelReader
from scfile.content.models import LocalBoneId, SkeletonBoneId
from scfile.content.models import ModelUnits as Units


def test_clip() -> None:
    values = np.array([0, 0, 0, 16384, 16384, -16384, 32767], dtype="<i2").view("<u2")

    with ModelReader(values.tobytes()) as reader:
        rotations, translations, weights = reader.clip(1, 1, 0, 2.0)

    assert rotations.shape == (1, 1, 4)
    assert np.allclose(translations[0, 0], [1.0, -1.0, 2.0], atol=1e-4)
    assert weights.shape == (1, 0)


def test_bone() -> None:
    values = np.arange(6, dtype="<f4")

    with ModelReader(values.tobytes()) as reader:
        position, tail = reader.bone()

    assert np.array_equal(position, values[:3])
    assert np.array_equal(tail, values[3:])


def test_vertex() -> None:
    values = np.array([16384, -16384, 0, 32767], dtype="<i2")

    with ModelReader(values.tobytes()) as reader:
        vertices = reader.vertex(F.I16, Factor.I16, Units.TEXTURES, 2, scale=2.0)

    assert vertices.shape == (2, 2)
    assert np.allclose(vertices, [[1.0, -1.0], [0.0, 2.0]], atol=1e-4)


def test_normals() -> None:
    values = np.array([127, 0, 0, 0, 0, 0, 0, 0], dtype=np.int8)

    with ModelReader(values.tobytes()) as reader:
        normals = reader.normals(2)

    assert np.allclose(normals, [[1.0, 0.0, 0.0], [0.0, 0.0, 0.0]])


def test_tangents() -> None:
    values = np.array([127, 0, 0, 1, 0, 127, 0, -1], dtype=np.int8)

    with ModelReader(values.tobytes()) as reader:
        tangents = reader.tangents(2)

    assert np.allclose(tangents, [[1.0, 0.0, 0.0, 1.0], [0.0, 1.0, 0.0, -1.0]])


def test_blend_shapes() -> None:
    values = np.array(
        [
            [128, 127, 127, 0],
            [255, 0, 127, 0],
        ],
        dtype=np.uint8,
    )

    with ModelReader(values.tobytes()) as reader:
        shapes = reader.blend_shapes(1, 2, np.array([1, 0], dtype=np.uint16))

    assert np.allclose(shapes[0, 0], [128 / 255, -127 / 255, 0.0])
    assert np.allclose(shapes[0, 1], [1 / 255, 0.0, 0.0])


def test_polygons() -> None:
    values = np.array([0, 1, 2, 3], dtype="<u2")

    with ModelReader(values.tobytes()) as reader:
        polygons = reader.polygons(1, quads=True)

    assert np.array_equal(polygons, [[0, 1, 2], [0, 2, 3]])


def test_triangles() -> None:
    values = np.array([0, 1, 2], dtype="<u2")

    with ModelReader(values.tobytes()) as reader:
        polygons = reader.polygons(1)

    assert np.array_equal(polygons, [[0, 1, 2]])


def test_links() -> None:
    mapping = {LocalBoneId(0): SkeletonBoneId(4), LocalBoneId(1): SkeletonBoneId(7)}
    values = np.array([0, 1, 0, 0, 64, 191, 0, 0], dtype=np.uint8)

    with ModelReader(values.tobytes()) as reader:
        ids, weights = reader.plain_links(1, mapping)

    assert np.array_equal(ids, [[4, 7, 0, 0]])
    assert np.isclose(weights.sum(), 1.0)
    assert np.isclose(weights[0, 0] / weights[0, 1], 64 / 191)


def test_packed_links() -> None:
    mapping = {LocalBoneId(0): SkeletonBoneId(4), LocalBoneId(1): SkeletonBoneId(7)}
    values = np.array([0, 1, 64, 191], dtype=np.uint8)

    with ModelReader(values.tobytes()) as reader:
        ids, weights = reader.packed_links(1, mapping)

    assert np.array_equal(ids, [[4, 7, 0, 0]])
    assert np.isclose(weights.sum(), 1.0)
    assert np.isclose(weights[0, 0] / weights[0, 1], 64 / 191)
