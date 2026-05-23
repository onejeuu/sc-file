"""
FBX Format.

:Type: Model Encoder
:Name: Autodesk Filmbox
:Wiki: `<https://en.wikipedia.org/wiki/FBX>`_

Example::

    from scfile import formats

    with formats.fbx.FbxEncoder(data) as fbx:
        fbx.encode().save("output.fbx")
"""

from .encoder import FbxEncoder


__all__ = ("FbxEncoder",)
