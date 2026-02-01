🧊 DAE
==========================

.. code-block:: python
  :caption: Usage Example

  from scfile import formats

  with formats.mcsb.McsbDecoder("path/to/model.mcsb") as mcsb:
    data = mcsb.decode()

  with formats.dae.DaeEncoder(data) as dae:
    dae.encode().save("output.dae")

Encoder
---------------------------------

.. automodule:: scfile.formats.dae.encoder
  :members:
  :show-inheritance:
  :undoc-members:
