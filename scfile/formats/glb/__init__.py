"""
GLB Format.

:Name: **glTF Binary**
:Handler: :class:`~scfile.formats.glb.encoder.GlbEncoder`
:Content: :class:`~scfile.content.base.ModelContent`
:Suffix: ``.glb``
:Support: ``✅ FULL``
:Features: ``UV``, ``UV2``, ``Normals``, ``Tangents``, ``Skeleton``, ``Blend Shapes``, ``Bone Animation``, ``Morph Animation``
:Wiki: https://en.wikipedia.org/wiki/GlTF

Usage Example::

    from scfile import formats

    with formats.GlbEncoder(data) as glb:
        glb.save("output.glb")
"""

from .encoder import GlbEncoder


__all__ = ("GlbEncoder",)
