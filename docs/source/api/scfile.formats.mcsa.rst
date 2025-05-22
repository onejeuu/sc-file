MCSA
===========================

.. automodule:: scfile.formats.mcsa
  :no-members:
  :show-inheritance:

.. code-block:: python
  :caption: Usage Example

  from scfile.formats.mcsa.decoder import McsaDecoder
  from scfile.formats.obj.encoder import ObjEncoder

  with McsaDecoder("path/to/model.mcsa") as mcsa:
    data = mcsa.decode()

    with ObjEncoder(data) as obj:
      obj.encode().save("output.obj")

Decoder
----------------------------------

.. automodule:: scfile.formats.mcsa.decoder
  :members:
  :show-inheritance:
  :undoc-members:

Exceptions
-------------------------------------

.. automodule:: scfile.formats.mcsa.exceptions
  :members:
  :show-inheritance:
  :undoc-members:

Flags
--------------------------------

.. automodule:: scfile.formats.mcsa.flags
  :members:
  :show-inheritance:
  :undoc-members:

IO
-----------------------------

.. automodule:: scfile.formats.mcsa.io
  :members:
  :show-inheritance:
  :undoc-members:
