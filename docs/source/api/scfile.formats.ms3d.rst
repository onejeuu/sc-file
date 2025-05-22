MS3D
===========================

.. automodule:: scfile.formats.ms3d
  :no-members:
  :show-inheritance:

.. code-block:: python
  :caption: Usage Example

  from scfile.formats.mcsb.decoder import McsbDecoder
  from scfile.formats.ms3d.encoder import Ms3dEncoder

  with McsbDecoder("path/to/model.mcsb") as mcsb:
    data = mcsb.decode()

    with Ms3dEncoder(data) as ms3d:
      ms3d.encode().save("output.ms3d")

Encoder
----------------------------------

.. automodule:: scfile.formats.ms3d.encoder
   :members:
   :show-inheritance:
   :undoc-members:

Exceptions
-------------------------------------

.. automodule:: scfile.formats.ms3d.exceptions
   :members:
   :show-inheritance:
   :undoc-members:

IO
-----------------------------

.. automodule:: scfile.formats.ms3d.io
   :members:
   :show-inheritance:
   :undoc-members:
