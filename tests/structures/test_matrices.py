import numpy as np
import pytest

from scfile.structures.models import matrices as M


def test_rot():
    result = M.create_rotation_matrix(np.array([0.0, 0.0, 0.0], dtype=np.float32))
    assert np.allclose(result, np.eye(3, dtype=np.float32))


def test_rot_x90():
    result = M.create_rotation_matrix(np.array([90.0, 0.0, 0.0], dtype=np.float32))
    v = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    expected = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    assert np.allclose(result @ v, expected, atol=1e-6)


def test_rot_y90():
    result = M.create_rotation_matrix(np.array([0.0, 90.0, 0.0], dtype=np.float32))
    v = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    expected = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    assert np.allclose(result @ v, expected, atol=1e-6)


def test_rot_z90():
    result = M.create_rotation_matrix(np.array([0.0, 0.0, 90.0], dtype=np.float32))
    v = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    expected = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    assert np.allclose(result @ v, expected, atol=1e-6)


def test_rot_order():
    angles = np.array([45.0, 45.0, 45.0], dtype=np.float32)
    result = M.create_rotation_matrix(angles)

    ax = M.create_rotation_matrix(np.array([45.0, 0.0, 0.0], dtype=np.float32))
    ay = M.create_rotation_matrix(np.array([0.0, 45.0, 0.0], dtype=np.float32))
    az = M.create_rotation_matrix(np.array([0.0, 0.0, 45.0], dtype=np.float32))

    expected = ax @ ay @ az
    assert np.allclose(result, expected, atol=1e-6)


def test_rot_orthogonal():
    rot = np.array([30.0, -45.0, 60.0], dtype=np.float32)
    result = M.create_rotation_matrix(rot)
    assert np.allclose(result @ result.T, np.eye(3), atol=1e-6)
    assert pytest.approx(np.linalg.det(result), rel=1e-6) == 1.0


def test_rot_vector_length():
    v = np.array([1.2, -3.4, 5.6], dtype=np.float32)
    rot = np.array([17.0, 42.0, -88.0], dtype=np.float32)
    result = M.create_rotation_matrix(rot)

    assert pytest.approx(np.linalg.norm(v)) == np.linalg.norm(result @ v)


def test_transform():
    result = M.create_transform_matrix(
        np.array([0.0, 0.0, 0.0], dtype=np.float32),
        np.array([0.0, 0.0, 0.0], dtype=np.float32),
    )
    assert np.allclose(result, np.eye(4, dtype=np.float32))


def test_transform_translation():
    result = M.create_transform_matrix(
        np.array([1.0, 2.0, 3.0], dtype=np.float32),
        np.array([0.0, 0.0, 0.0], dtype=np.float32),
    )
    assert np.allclose(result[:3, 3], [1.0, 2.0, 3.0])
    assert np.allclose(result[:3, :3], np.eye(3))


def test_transform_rot_and_trans():
    result = M.create_transform_matrix(
        np.array([10.0, 20.0, 30.0], dtype=np.float32),
        np.array([0.0, 0.0, 90.0], dtype=np.float32),
    )
    assert np.allclose(result[:3, 3], [10.0, 20.0, 30.0])
    assert result[3, 3] == 1.0
    assert result[3, 0] == 0.0


def test_transform_inverse():
    pos = np.array([1.0, -2.0, 3.0], dtype=np.float32)
    rot = np.array([30.0, 60.0, 90.0], dtype=np.float32)
    mat = M.create_transform_matrix(pos, rot)
    inv_mat = np.linalg.inv(mat)

    assert np.allclose(mat @ inv_mat, np.eye(4), atol=1e-5)


def test_handedness():
    result = M.create_rotation_matrix(np.array([0.0, 0.0, 90.0], dtype=np.float32))
    v = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    rotated = result @ v

    cross_product = np.cross(v, rotated)
    assert np.allclose(cross_product, [0.0, 0.0, 1.0], atol=1e-6)


def test_quat():
    result = M.euler_to_quat(np.array([0.0, 0.0, 0.0], dtype=np.float32))
    assert np.allclose(result, [0.0, 0.0, 0.0, 1.0])


def test_quat_x90():
    result = M.euler_to_quat(np.array([90.0, 0.0, 0.0], dtype=np.float32))
    expected = np.array([np.sin(np.pi / 4), 0.0, 0.0, np.cos(np.pi / 4)], dtype=np.float32)
    assert np.allclose(result, expected)


def test_quat_y180():
    result = M.euler_to_quat(np.array([0.0, 180.0, 0.0], dtype=np.float32))
    assert np.allclose(result, [0.0, 1.0, 0.0, 0.0], atol=1e-6)


def test_quat_unit():
    result = M.euler_to_quat(np.array([30.0, -45.0, 60.0], dtype=np.float32))
    assert pytest.approx(np.linalg.norm(result), rel=1e-6) == 1.0
