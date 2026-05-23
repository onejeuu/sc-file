"""
DAE Format.

:Type: Model Encoder
:Name: COLLADA
:Wiki: `<https://en.wikipedia.org/wiki/COLLADA>`_

Example::

    from scfile import formats

    with formats.dae.DaeEncoder(data) as dae:
        dae.encode().save("output.dae")
"""

from .encoder import DaeEncoder


__all__ = ("DaeEncoder",)
