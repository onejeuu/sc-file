🧊 MCSA
===========================

.. code-block:: python
  :caption: Usage Example

  from scfile import formats

  with formats.mcsa.McsaDecoder("path/to/model.mcsa") as mcsa:
    data = mcsa.decode()

  with formats.obj.ObjEncoder(data) as obj:
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

IO
-----------------------------

.. automodule:: scfile.formats.mcsa.io
  :members:
  :show-inheritance:
  :undoc-members:
