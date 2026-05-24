"""
JSON Format.

:Name: **JavaScript Object Notation**
:Type: **⚙️ NBT Encoder**
:Wiki: `<https://en.wikipedia.org/wiki/JSON>`_
:Suffix: ``.json``
:Support: ``✅ Full``

Example::

    from scfile import formats

    with formats.json.JsonEncoder(data) as json:
        json.encode().save("output.json")
"""

from .encoder import JsonEncoder


__all__ = ("JsonEncoder",)
