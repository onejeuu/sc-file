📦 TEXARR
=============================

.. code-block:: python
  :caption: Usage Example

  from scfile import formats

  with formats.texarr.TextureArrayDecoder("path/to/blockMap.texarr") as ta:
    data = ta.decode()

  with formats.zip.TextureArrayEncoder(data) as zip:
    zip.encode().save("output.zip")

Decoder
---------------------------------

.. automodule:: scfile.formats.texarr.decoder
   :members:
   :show-inheritance:
   :undoc-members:
