MIC
==========================

.. automodule:: scfile.formats.mic
  :no-members:
  :show-inheritance:

.. code-block:: python
  :caption: Usage Example

  from scfile.formats.mic.decoder import MicDecoder
  from scfile.formats.png.encoder import PngEncoder

  with MicDecoder("path/to/image.mic") as mic:
    data = mic.decode()

    with PngEncoder(data) as png:
      png.encode().save("output.png")

Decoder
---------------------------------

.. automodule:: scfile.formats.mic.decoder
  :members:
  :show-inheritance:
  :undoc-members:
