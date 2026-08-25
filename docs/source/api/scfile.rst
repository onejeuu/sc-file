API Reference
==================================================

.. automodule:: scfile
   :no-members:

Modules
-------

.. toctree::
   :maxdepth: 2

   scfile.convert
   scfile.formats
   scfile.content
   scfile.core
   scfile.io

Consts
------

.. automodule:: scfile.consts
   :members:
   :show-inheritance:
   :undoc-members:

Enums
-----

.. automodule:: scfile.enums
   :members:
   :show-inheritance:
   :undoc-members:

Exceptions
----------

.. automodule:: scfile.exceptions
   :members:
   :show-inheritance:
   :undoc-members:

Options
-------

.. automodule:: scfile.options
   :members:
   :show-inheritance:
   :undoc-members:

.. py:type:: TargetConfig
   :module: scfile.options

   ``Mapping[type[BaseContent], FileFormat]``

   Requested conversion targets by content type.

Types
-----

.. automodule:: scfile.types
   :members:
   :show-inheritance:
   :undoc-members:

.. py:type:: PathLike
   :module: scfile.types

   ``str | Path | os.PathLike[str]``

   Path represented as a string, pathlib path, or OS path-like object.

.. py:type:: SourcePath
   :module: scfile.types

   ``Path``

   Source path.

.. py:type:: SourceLike
   :module: scfile.types

   ``PathLike``

   Source path-like.

.. py:type:: OutputPath
   :module: scfile.types

   ``Path | None``

   Optional output path.

.. py:type:: OutputLike
   :module: scfile.types

   ``PathLike | None``

   Optional path-like output.

.. py:type:: ResultPath
   :module: scfile.types

   ``Path | None``

   Written result path, or ``None`` when output is skipped.

.. py:type:: Formats
   :module: scfile.types

   ``Sequence[FileFormat]``

   Sequence of file formats.

.. py:type:: FormatLike
   :module: scfile.types

   ``str | FileFormat``

   File format represented by its enum, value, or suffix.
