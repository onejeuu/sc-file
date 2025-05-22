GLB
==========================

.. automodule:: scfile.formats.glb
  :no-members:
  :show-inheritance:

.. code-block:: python
  :caption: Usage Example

  from scfile.formats.mcsb.decoder import McsbDecoder
  from scfile.formats.glb.encoder import GlbEncoder

  with McsbDecoder("path/to/model.mcsb") as mcsb:
    data = mcsb.decode()

    with GlbEncoder(data) as glb:
      glb.encode().save("output.glb")

Encoder
---------------------------------

.. automodule:: scfile.formats.glb.encoder
  :members:
  :show-inheritance:
  :undoc-members:

Enums
-------------------------------

.. automodule:: scfile.formats.glb.enums
  :members:
  :show-inheritance:
  :undoc-members:
