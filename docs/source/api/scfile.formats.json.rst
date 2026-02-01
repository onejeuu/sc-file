⚙️ JSON
===========================

.. code-block:: python
  :caption: Usage Example

  from scfile import formats

  with formats.nbt.NbtDecoder("path/to/itemnames.dat") as nbt:
    data = nbt.decode()

  with formats.json.JsonEncoder(data) as json:
    json.encode().save("output.json")

Encoder
----------------------------------

.. automodule:: scfile.formats.json.encoder
  :members:
  :show-inheritance:
  :undoc-members:
