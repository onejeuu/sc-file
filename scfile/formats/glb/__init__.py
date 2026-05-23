"""
GLB Format.

:Type: Model Encoder
:Name: gLTF (Graphics Library Transmission Format)
:Wiki: `<https://en.wikipedia.org/wiki/GlTF>`_

Example::

    from scfile import formats

    with formats.glb.GlbEncoder(data) as glb:
        glb.encode().save("output.glb")
"""

from .encoder import GlbEncoder


__all__ = ("GlbEncoder",)
