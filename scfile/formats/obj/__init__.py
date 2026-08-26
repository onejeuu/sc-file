"""
OBJ Format.

:Name: **Wavefront OBJ**
:Handler: :class:`~scfile.formats.obj.encoder.ObjEncoder`
:Content: :class:`~scfile.content.base.ModelContent`
:Suffix: ``.obj``
:Support: ``✅ FULL``
:Features: ``UV``, ``Normals``
:Wiki: `<https://en.wikipedia.org/wiki/Wavefront_.obj_file>`_

Usage Example::

    from scfile import formats

    with formats.ObjEncoder(data) as obj:
        obj.save("output.obj")
"""

from .encoder import ObjEncoder


__all__ = ("ObjEncoder",)
