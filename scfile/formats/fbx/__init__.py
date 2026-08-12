"""
FBX Format.

:Name: **Autodesk Filmbox**
:Type: **🧊 Model Encoder**
:Wiki: `<https://en.wikipedia.org/wiki/FBX>`_
:Suffix: ``.fbx``
:Support: ``⚠️ Partial``
:Features: ``UV``, ``UV2``, ``Normals``, ``Skeleton``, ``Bone Animation``

Example::

    from scfile import formats

    with formats.fbx.FbxEncoder(data) as fbx:
        fbx.encode().save("output.fbx")
"""

from .encoder import FbxEncoder


__all__ = ("FbxEncoder",)
