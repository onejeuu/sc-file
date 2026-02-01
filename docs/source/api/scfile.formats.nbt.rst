⚙️ NBT
==========================

.. code-block:: python
  :caption: Usage Example

  from scfile import formats

  with formats.nbt.NbtDecoder("path/to/itemnames.dat") as nbt:
    data = nbt.decode()

  with formats.json.JsonEncoder(data) as json:
    json.encode().save("output.json")

Decoder
---------------------------------

.. automodule:: scfile.formats.nbt.decoder
  :members:
  :show-inheritance:
  :undoc-members:

Enums
-------------------------------

.. automodule:: scfile.formats.nbt.enums
  :members:
  :show-inheritance:
  :undoc-members:

IO
----------------------------

.. automodule:: scfile.formats.nbt.io
  :members:
  :show-inheritance:
  :undoc-members:
