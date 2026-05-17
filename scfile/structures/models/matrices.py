import numpy as np

from .types import EulerAngles, Quaternion, RotationMatrix, TransformMatrix, Vector3D


def create_rotation_matrix(rotation: EulerAngles) -> RotationMatrix:
    angles = np.radians(rotation)
    cx, cy, cz = np.cos(angles)
    sx, sy, sz = np.sin(angles)

    return np.array(
        [
            [cy * cz, -cy * sz, sy],
            [cx * sz + cz * sx * sy, cx * cz - sx * sy * sz, -cy * sx],
            [sx * sz - cx * cz * sy, cz * sx + cx * sy * sz, cx * cy],
        ],
        dtype=np.float32,
    )


def create_transform_matrix(position: Vector3D, rotation: EulerAngles) -> TransformMatrix:
    matrix = np.eye(4, dtype=np.float32)
    matrix[:3, :3] = create_rotation_matrix(rotation)
    matrix[:3, 3] = position
    return matrix


def euler_to_quat(rotation: EulerAngles) -> Quaternion:
    x, y, z = np.radians(rotation)
    hx, hy, hz = x * 0.5, y * 0.5, z * 0.5

    cx, cy, cz = np.cos([hx, hy, hz])
    sx, sy, sz = np.sin([hx, hy, hz])

    return np.array(
        [
            sx * cy * cz - cx * sy * sz,
            cx * sy * cz + sx * cy * sz,
            cx * cy * sz - sx * sy * cz,
            cx * cy * cz + sx * sy * sz,
        ],
        dtype=np.float32,
    )
