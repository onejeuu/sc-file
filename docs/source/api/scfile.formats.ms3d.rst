🧊 MS3D
===========================

.. code-block:: python
  :caption: Usage Example

  from scfile import formats

  with formats.mcsb.McsbDecoder("path/to/model.mcsb") as mcsb:
    data = mcsb.decode()

  with formats.ms3d.Ms3dEncoder(data) as ms3d:
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
