"""
DAE Format.

:Name: **COLLADA**
:Type: **🧊 Model Encoder**
:Wiki: `<https://en.wikipedia.org/wiki/COLLADA>`_
:Suffix: ``.dae``
:Support: ``⚠️ Partial``
:Features: ``Geometry``, ``Skeleton``

Example::

    from scfile import formats

    with formats.dae.DaeEncoder(data) as dae:
        dae.encode().save("output.dae")
"""

from .encoder import DaeEncoder


__all__ = ("DaeEncoder",)
