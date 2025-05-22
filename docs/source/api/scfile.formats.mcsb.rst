MCSB
===========================

.. automodule:: scfile.formats.mcsb
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

Decoder
----------------------------------

.. automodule:: scfile.formats.mcsb.decoder
  :members:
  :show-inheritance:
  :undoc-members:
