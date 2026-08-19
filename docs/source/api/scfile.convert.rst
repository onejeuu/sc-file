🔄 Convert
==================================================

.. automodule:: scfile.convert
   :no-members:

Animate
-------

.. automodule:: scfile.convert.animate
   :members:
   :show-inheritance:
   :undoc-members:

Files
-----

.. automodule:: scfile.convert.files
   :members:
   :show-inheritance:
   :undoc-members:

Formats
-------

.. automodule:: scfile.convert.formats
   :members:
   :show-inheritance:
   :undoc-members:

Mapcache
--------

.. automodule:: scfile.convert.mapcache
   :members:
   :show-inheritance:
   :undoc-members:

.. py:type:: RegionKey
   :module: scfile.convert.mapcache

   ``tuple[int, int]``

.. py:type:: Regions
   :module: scfile.convert.mapcache

   ``dict[RegionKey, list[Path]]``

.. py:type:: CancelCheck
   :module: scfile.convert.mapcache

   ``Callable[[], bool] | None``

Named
-----

.. automodule:: scfile.convert.named
   :members:
   :show-inheritance:
   :undoc-members:

.. py:type:: Converter
   :module: scfile.convert.named

   ``Callable[[SourceLike, OutputLike, Optional[Options]], ResultPath]``

Paths
-----

.. automodule:: scfile.convert.paths
   :members:
   :show-inheritance:
   :undoc-members:
