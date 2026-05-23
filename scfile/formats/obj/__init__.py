"""
OBJ Format.

:Type: Model Encoder
:Name: Wavefront OBJ
:Wiki: `<https://en.wikipedia.org/wiki/Wavefront_.obj_file>`_

Example::

    from scfile import formats

    with formats.obj.ObjEncoder(data) as obj:
        obj.encode().save("output.obj")
"""

from .encoder import ObjEncoder


__all__ = ("ObjEncoder",)
