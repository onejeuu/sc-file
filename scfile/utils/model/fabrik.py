import numpy as np
from scipy.spatial.transform import Rotation as R

from scfile.utils.model.data import Vector
from scfile.utils.model.skeleton import ROOT, ModelSkeleton, SkeletonBone


class InverseKinematics:
    def __init__(self, skeleton: ModelSkeleton, max_iterations: int = 10, tolerance: float = 0.01):
        self.skeleton = skeleton
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def build(self, end_effector_id: int, target_position: Vector) -> bool:
        bones = self.skeleton.bones
        current_bone = bones[end_effector_id]

        # Build bone chain from end effector to root
        chain = []
        while current_bone.parent_id != ROOT:
            chain.append(current_bone)
            current_bone = bones[current_bone.parent_id]
        chain.append(current_bone)

        for iteration in range(self.max_iterations):
            # Get current end effector position in world space
            end_pos = self._get_world_position(bones[end_effector_id])

            # Check if we've reached the target within tolerance
            if self._distance(end_pos, target_position) < self.tolerance:
                return True

            # Process each bone in the chain from end effector to root
            for bone in chain:
                # Get current bone position in world space
                joint_pos = self._get_world_position(bone)

                # Calculate vectors to target and current end effector
                to_target = target_position - joint_pos
                to_end = end_pos - joint_pos

                # Calculate required rotation angle
                angle = self._calculate_rotation_angle(to_target, to_end)

                # Apply rotation if significant enough
                if abs(angle) > 0.001:  # Avoid micro-rotations
                    # Calculate rotation axis using cross product
                    rotation_axis = np.cross(list(to_end), list(to_target))
                    if np.any(rotation_axis):  # Check if rotation axis is valid
                        # Normalize rotation axis and create rotation
                        rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
                        rotation = R.from_rotvec(angle * rotation_axis)
                        euler_angles = rotation.as_euler("xyz", degrees=True)

                        # Update bone rotation
                        bone.rotation = Vector(
                            bone.rotation.x + euler_angles[0],
                            bone.rotation.y + euler_angles[1],
                            bone.rotation.z + euler_angles[2],
                        )

                        # Update end effector position after rotation
                        end_pos = self._get_world_position(bones[end_effector_id])

        return False

    def _get_world_position(self, bone: SkeletonBone) -> Vector:
        """Calculate the world space position of a bone."""
        position = bone.position
        current = bone

        while current.parent_id != ROOT:
            parent = self.skeleton.bones[current.parent_id]
            # Apply parent rotation and position
            parent_rotation = R.from_euler("xyz", list(parent.rotation), degrees=True)
            rotated_position = parent_rotation.apply(list(position))
            position = Vector(*rotated_position) + parent.position
            current = parent

        return position

    def _distance(self, v1: Vector, v2: Vector) -> float:
        """Calculate Euclidean distance between two vectors."""
        return np.sqrt((v1.x - v2.x) ** 2 + (v1.y - v2.y) ** 2 + (v1.z - v2.z) ** 2)

    def _calculate_rotation_angle(self, v1: Vector, v2: Vector) -> float:
        """Calculate the angle between two vectors."""
        v1_np = np.array(list(v1))
        v2_np = np.array(list(v2))

        v1_norm = np.linalg.norm(v1_np)
        v2_norm = np.linalg.norm(v2_np)

        if v1_norm == 0 or v2_norm == 0:
            return 0.0

        cos_angle = np.dot(v1_np, v2_np) / (v1_norm * v2_norm)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Avoid numerical errors
        return np.arccos(cos_angle)
