ZIP
=============================

.. automodule:: scfile.formats.zip
  :members:
  :show-inheritance:
  :undoc-members:

.. code-block:: python
  :caption: Usage Example

  from scfile.formats.texarr.decoder import TextureArrayDecoder
  from scfile.formats.zip.encoder import TextureArrayEncoder

  with TextureArrayDecoder("path/to/blocks.texarr") as ta:
    data = ta.decode()

    with TextureArrayEncoder(data) as zip:
      zip.encode().save("output.zip")

Decoder
---------------------------------

.. automodule:: scfile.formats.zip.encoder
   :members:
   :show-inheritance:
   :undoc-members:
