"""
FBX Format.

:Name: **Autodesk Filmbox**
:Handler: :class:`~scfile.formats.fbx.encoder.FbxEncoder`
:Content: :class:`~scfile.content.base.ModelContent`
:Suffix: ``.fbx``
:Support: ``⚠️ PARTIAL``
:Features: ``UV``, ``UV2``, ``Normals``, ``Skeleton``, ``Bone Animation``
:Wiki: https://en.wikipedia.org/wiki/FBX

Usage Example::

    from scfile import formats

    with formats.FbxEncoder(data) as fbx:
        fbx.save("output.fbx")
"""

from .encoder import FbxEncoder


__all__ = ("FbxEncoder",)
