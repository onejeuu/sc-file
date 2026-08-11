"""
MCVD Format.

:Name: **Vector Dynamic**
:Type: **🧊 Model Decoder**
:Wiki: `https://sc-file.rtfd.io/formats.html <https://sc-file.rtfd.io/en/latest/formats.html#mcvd-vector-dynamic-mcsa-bt>`_
:Suffix: ``.mcvd``
:Support: ``✅ Full``
:Features: ``UV``, ``UV2``, ``Normals``, ``Tangents``, ``Skeleton``, ``Blend Shapes``, ``Bone Animation``, ``Morph Animation``

Example::

    from scfile import formats

    with formats.mcvd.McvdDecoder("animation.mcvd") as mcvd:
        data = mcvd.decode()
"""

from .decoder import McvdDecoder


__all__ = ("McvdDecoder",)
