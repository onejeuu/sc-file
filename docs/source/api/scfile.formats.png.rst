🖼️ PNG
==========================

.. code-block:: python
  :caption: Usage Example

  from scfile import formats

  with formats.mic.MicDecoder("path/to/image.mic") as mic:
    data = mic.decode()

  with formats.png.PngEncoder(data) as png:
    png.encode().save("output.png")

Encoder
---------------------------------

.. automodule:: scfile.formats.png.encoder
  :members:
  :show-inheritance:
  :undoc-members:
