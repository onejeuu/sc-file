🗃️ Structures
==================================================

.. automodule:: scfile.structures
   :no-members:

Modules
-------

.. toctree::
   :maxdepth: 2

   scfile.structures.models

Content
-------

.. automodule:: scfile.structures.content
   :members:
   :show-inheritance:
   :undoc-members:

.. py:type:: DocumentPrimitive
   :module: scfile.structures.content

   ``int | float | bytes | str``

.. py:type:: DocumentValue
   :module: scfile.structures.content

   ``None | DocumentPrimitive | list[DocumentValue] | dict[str, DocumentValue]``

.. py:type:: ArchiveEntry
   :module: scfile.structures.content

   ``tuple[str, bytes]``

Regions
-------

.. automodule:: scfile.structures.regions
   :members:
   :show-inheritance:
   :undoc-members:

Textures
--------

.. automodule:: scfile.structures.textures
   :members:
   :show-inheritance:
   :undoc-members:
