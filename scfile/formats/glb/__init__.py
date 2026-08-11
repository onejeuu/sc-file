"""
GLB Format.

:Name: **glTF Binary**
:Type: **🧊 Model Encoder**
:Wiki: `<https://en.wikipedia.org/wiki/GlTF>`_
:Suffix: ``.glb``
:Support: ``✅ Full``
:Features: ``UV``, ``UV2``, ``Normals``, ``Tangents``, ``Skeleton``, ``Blend Shapes``, ``Bone Animation``, ``Morph Animation``

Example::

    from scfile import formats

    with formats.glb.GlbEncoder(data) as glb:
        glb.encode().save("output.glb")
"""

from .encoder import GlbEncoder


__all__ = ("GlbEncoder",)
