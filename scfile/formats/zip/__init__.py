"""
ZIP Format.

:Name: **ZIP**
:Handler: :class:`~scfile.formats.zip.encoder.ZipEncoder`
:Content: :class:`~scfile.content.base.ArchiveContent`
:Suffix: ``.zip``
:Support: ``✅ FULL``
:Wiki: `<https://en.wikipedia.org/wiki/ZIP_(file_format)>`_

Usage Example::

    from scfile import formats

    with formats.ZipEncoder(data) as zip:
        zip.save("output.zip")
"""

from .encoder import ZipEncoder


__all__ = ("ZipEncoder",)
