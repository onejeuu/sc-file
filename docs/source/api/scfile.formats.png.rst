PNG
==========================

.. automodule:: scfile.formats.png
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

Encoder
---------------------------------

.. automodule:: scfile.formats.png.encoder
  :members:
  :show-inheritance:
  :undoc-members:
