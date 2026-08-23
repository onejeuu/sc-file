🗃️ Structures
==================================================

.. automodule:: scfile.content
   :no-members:

Modules
-------

.. toctree::
   :maxdepth: 2

   scfile.content.models

Content
-------

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

Regions
-------

.. automodule:: scfile.content.regions
   :members:
   :show-inheritance:
   :undoc-members:

Textures
--------

.. automodule:: scfile.content.textures
   :members:
   :show-inheritance:
   :undoc-members:
