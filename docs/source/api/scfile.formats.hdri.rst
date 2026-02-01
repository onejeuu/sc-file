🧱 OL (CUBEMAP)
===========================

.. code-block:: python
  :caption: Usage Example

  from scfile import formats

  with formats.hdri.OlCubemapDecoder("path/to/texture.ol") as hdri:
    data = hdri.decode()

  with formats.dds.DdsEncoder(data) as dds:
    dds.encode().save("output.dds")

Decoder
----------------------------------

.. automodule:: scfile.formats.hdri.decoder
  :members:
  :show-inheritance:
  :undoc-members:
