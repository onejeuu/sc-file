DDS
==========================

.. automodule:: scfile.formats.dds
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

Encoder
---------------------------------

.. automodule:: scfile.formats.dds.encoder
  :members:
  :show-inheritance:
  :undoc-members:

Enums
-------------------------------

.. automodule:: scfile.formats.dds.enums
   :members:
   :show-inheritance:
   :undoc-members:

Header
--------------------------------

.. automodule:: scfile.formats.dds.header
  :members:
  :show-inheritance:
  :undoc-members:
