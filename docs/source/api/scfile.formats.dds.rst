🧱 DDS
==========================

.. code-block:: python
  :caption: Usage Example

  from scfile import formats

  with formats.ol.OlDecoder("path/to/texture.ol") as ol:
    data = ol.decode()

  with formats.dds.DdsEncoder(data) as dds:
    dds.encode().save("output.dds")

Encoder
---------------------------------

.. automodule:: scfile.formats.dds.encoder
  :members:
  :show-inheritance:
  :undoc-members:
