DAE
==========================

.. automodule:: scfile.formats.dae
  :members:
  :show-inheritance:
  :undoc-members:

.. code-block:: python
  :caption: Usage Example

  from scfile.formats.mcsb.decoder import McsbDecoder
  from scfile.formats.dae.encoder import DaeEncoder

  with McsbDecoder("path/to/model.mcsb") as mcsb:
    data = mcsb.decode()

    with DaeEncoder(data) as dae:
      dae.encode().save("output.dae")

Encoder
---------------------------------

.. automodule:: scfile.formats.dae.encoder
  :members:
  :show-inheritance:
  :undoc-members:
