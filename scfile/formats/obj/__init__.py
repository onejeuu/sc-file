"""
OBJ Format.

:Name: **Wavefront OBJ**
:Type: **🧊 Model Encoder**
:Wiki: `<https://en.wikipedia.org/wiki/Wavefront_.obj_file>`_
:Suffix: ``.obj``
:Support: ``✅ Full``
:Features: ``Geometry``

Example::

    from scfile import formats

    with formats.obj.ObjEncoder(data) as obj:
        obj.encode().save("output.obj")
"""

from .encoder import ObjEncoder


__all__ = ("ObjEncoder",)
