🧊 MCSB
===========================

.. code-block:: python
  :caption: Usage Example

  from scfile import formats

  with formats.mcsb.McsbDecoder("path/to/model.mcsb") as mcsb:
    data = mcsb.decode()

  with formats.obj.ObjEncoder(data) as obj:
    obj.encode().save("output.obj")

Decoder
----------------------------------

.. automodule:: scfile.formats.mcsb.decoder
  :members:
  :show-inheritance:
  :undoc-members:
