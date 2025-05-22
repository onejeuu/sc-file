OL
=========================

.. automodule:: scfile.formats.ol
  :no-members:
  :show-inheritance:

.. code-block:: python
  :caption: Usage Example

  from scfile.formats.ol.decoder import OlDecoder
  from scfile.formats.dds.encoder import DdsEncoder

  with OlDecoder("path/to/texture.ol") as ol:
    data = ol.decode()

    with DdsEncoder(data) as dds:
      dds.encode().save("output.dds")

Decoder
--------------------------------

.. automodule:: scfile.formats.ol.decoder
  :members:
  :show-inheritance:
  :undoc-members:

Exceptions
-----------------------------------

.. automodule:: scfile.formats.ol.exceptions
  :members:
  :show-inheritance:
  :undoc-members:

IO
---------------------------

.. automodule:: scfile.formats.ol.io
  :members:
  :show-inheritance:
  :undoc-members:
