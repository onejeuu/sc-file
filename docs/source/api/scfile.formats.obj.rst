OBJ
==========================

.. automodule:: scfile.formats.obj
  :no-members:
  :show-inheritance:

.. code-block:: python
  :caption: Usage Example

  from scfile.formats.mcsb.decoder import McsbDecoder
  from scfile.formats.obj.encoder import ObjEncoder

  with McsbDecoder("path/to/model.mcsb") as mcsb:
    data = mcsb.decode()

    with ObjEncoder(data) as obj:
      obj.encode().save("output.obj")

Encoder
---------------------------------

.. automodule:: scfile.formats.obj.encoder
  :members:
  :show-inheritance:
  :undoc-members:
