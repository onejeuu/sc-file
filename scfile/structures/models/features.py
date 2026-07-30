"""Model feature inspection."""

from typing import TYPE_CHECKING, assert_never

from .enums import Feature


if TYPE_CHECKING:
    from .scene import ModelScene


def has(
    scene: "ModelScene",
    feature: Feature,
) -> bool:
    """Return whether scene contains a feature."""

    match feature:
        case Feature.UV:
            return any(mesh.uv1.size for mesh in scene.meshes)

        case Feature.UV2:
            return any(mesh.uv2.size for mesh in scene.meshes)

        case Feature.NORMALS:
            return any(mesh.normals.size for mesh in scene.meshes)

        case Feature.TANGENTS:
            return any(mesh.tangents.size for mesh in scene.meshes)

        case Feature.COLORS:
            return any(mesh.colors.size for mesh in scene.meshes)

        case Feature.SKELETON:
            return bool(scene.skeleton.bones)

        case Feature.BLEND_SHAPES:
            return any(mesh.blend_shapes for mesh in scene.meshes)

        case Feature.ANIMATION:
            return any(has(scene, member) for member in feature.members)

        case Feature.BONE_ANIMATION:
            return any(clip.translations.size and clip.rotations.size for clip in scene.animation.clips)

        case Feature.MORPH_ANIMATION:
            return any(clip.morph_weights.size for clip in scene.animation.clips)

        case _:
            assert_never(feature)
