🧱 OL
=========================

.. code-block:: python
  :caption: Usage Example

  from scfile import formats

  with formats.ol.OlDecoder("path/to/texture.ol") as ol:
    data = ol.decode()

  with formats.dds.DdsEncoder(data) as dds:
    dds.encode().save("output.dds")

Decoder
--------------------------------

.. automodule:: scfile.formats.ol.decoder
  :members:
  :show-inheritance:
  :undoc-members:

Exceptions
-----------------------------------

.. automodule:: scfile.formats.ol.exceptions
  :members:
  :show-inheritance:
  :undoc-members:

IO
---------------------------

.. automodule:: scfile.formats.ol.io
  :members:
  :show-inheritance:
  :undoc-members:
