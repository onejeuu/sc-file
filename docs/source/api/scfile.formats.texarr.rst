TEXARR
=============================

.. automodule:: scfile.formats.texarr
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

.. automodule:: scfile.formats.texarr.decoder
   :members:
   :show-inheritance:
   :undoc-members:
