import numpy as np

from scfile.structures.models import create_rotation_matrix, create_transform_matrix, euler_to_quat, quaternions_to_euler


def test_rotation() -> None:
    matrix = create_rotation_matrix(np.zeros(3, dtype=np.float32))

    assert np.allclose(matrix, np.eye(3, dtype=np.float32))


def test_rotation_order() -> None:
    angles = np.array([45.0, 45.0, 45.0], dtype=np.float32)
    x = create_rotation_matrix(np.array([45.0, 0.0, 0.0], dtype=np.float32))
    y = create_rotation_matrix(np.array([0.0, 45.0, 0.0], dtype=np.float32))
    z = create_rotation_matrix(np.array([0.0, 0.0, 45.0], dtype=np.float32))

    assert np.allclose(create_rotation_matrix(angles), x @ y @ z)


def test_transform() -> None:
    translation = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    matrix = create_transform_matrix(translation, np.zeros(3, dtype=np.float32))

    assert np.allclose(matrix[:3, 3], translation)
    assert np.allclose(matrix[:3, :3], np.eye(3, dtype=np.float32))


def test_quaternion() -> None:
    quaternion = euler_to_quat(np.zeros(3, dtype=np.float32))

    assert np.allclose(quaternion, [0.0, 0.0, 0.0, 1.0])
    assert np.isclose(np.linalg.norm(quaternion), 1.0)


def test_quaternion_keyframes() -> None:
    angles = np.array([[27.0, -3.0, 5.0], [25.0, 6.0, 21.0], [-15.0, 9.0, 42.0]], dtype=np.float32)
    rotations = np.array([euler_to_quat(angle) for angle in angles])

    assert np.allclose(quaternions_to_euler(rotations), angles)
