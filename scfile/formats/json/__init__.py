"""
JSON Format.

:Name: **JavaScript Object Notation**
:Handler: :class:`~scfile.formats.json.encoder.JsonEncoder`
:Content: :class:`~scfile.content.base.DocumentContent`
:Suffix: ``.json``
:Support: ``✅ FULL``
:Wiki: https://en.wikipedia.org/wiki/JSON

Usage Example::

    from scfile import formats

    with formats.JsonEncoder(data) as json:
        json.save("output.json")
"""

from .encoder import JsonEncoder


__all__ = ("JsonEncoder",)
