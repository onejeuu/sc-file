"""
ZIP Format.

:Name: **ZIP**
:Type: **🗃️ Archive Encoder**
:Wiki: `<https://en.wikipedia.org/wiki/ZIP_(file_format)>`_
:Suffix: ``.zip``
:Support: ``✅ Full``

Example::

    from scfile import formats

    with formats.zip.ZipEncoder(data) as zip:
        zip.encode().save("output.zip")
"""

from .encoder import ZipEncoder


__all__ = ("ZipEncoder",)
