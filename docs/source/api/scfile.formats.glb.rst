🧊 GLB
==========================

.. code-block:: python
  :caption: Usage Example

  from scfile import formats

  with formats.mcsb.McsbDecoder("path/to/model.mcsb") as mcsb:
    data = mcsb.decode()

  with formats.glb.GlbEncoder(data) as glb:
    glb.encode().save("output.glb")

Encoder
---------------------------------

.. automodule:: scfile.formats.glb.encoder
  :members:
  :show-inheritance:
  :undoc-members:
