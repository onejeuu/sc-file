"""
JSON Format.

:Type: NBT Encoder
:Name: JavaScript Object Notation
:Wiki: `<https://en.wikipedia.org/wiki/JSON>`_

Example::

    from scfile import formats

    with formats.json.JsonEncoder(data) as json:
        json.encode().save("output.json")
"""

from .encoder import JsonEncoder


__all__ = ("JsonEncoder",)
