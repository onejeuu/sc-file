HDRI
===========================

.. automodule:: scfile.formats.hdri
  :no-members:
  :show-inheritance:

.. code-block:: python
  :caption: Usage Example

  from scfile.formats.hdri.decoder import OlCubemapDecoder
  from scfile.formats.dds.encoder import DdsEncoder

  with OlCubemapDecoder("path/to/texture.ol") as hdri:
    data = hdri.decode()

    with DdsEncoder(data) as dds:
      dds.encode().save("output.dds")

Decoder
----------------------------------

.. automodule:: scfile.formats.hdri.decoder
  :members:
  :show-inheritance:
  :undoc-members:
