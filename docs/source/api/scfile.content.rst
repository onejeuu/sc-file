🗃️ Content
==================================================

.. automodule:: scfile.content
   :no-members:

Base
-----

.. automodule:: scfile.content.base
   :members:
   :show-inheritance:
   :undoc-members:

.. py:type:: DocumentPrimitive
   :module: scfile.content.base

   ``int | float | bytes | str``

.. py:type:: DocumentValue
   :module: scfile.content.base

   ``None | DocumentPrimitive | list[DocumentValue] | dict[str, DocumentValue]``

.. py:type:: ArchiveEntry
   :module: scfile.content.base

   ``tuple[str, bytes]``

🧊 Models
-----------

.. toctree::
  :maxdepth: 2

  scfile.content.models

🗺 Regions
-----------

.. automodule:: scfile.content.regions
   :members:
   :show-inheritance:
   :undoc-members:

🧱 Textures
------------

.. automodule:: scfile.content.textures
   :members:
   :show-inheritance:
   :undoc-members:
