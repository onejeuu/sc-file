🔄 Converter
==================================================

.. include:: ../_links.rst


| :ref:`convert <cli-convert>` converts supported standalone files.
| Several files and directories can be processed in one operation.
| Directories are scanned recursively.


----------------------------------------
Standalone files
----------------------------------------

A standalone file contains enough data for independent export.
No additional files or other metadata are required to convert it.

.. list-table::
  :header-rows: 1

  * - Type
    - Sources
    - Output
  * - 🧊 Model
    - ``.mcsa``, ``.mcsb``, ``.mcvd``, ``.efkmodel``
    - ``.obj`` / ``.glb`` / ``.fbx``
  * - 🧱 Texture
    - ``.ol``
    - ``.dds``
  * - 🖼️ Image
    - ``.mic``
    - ``.png``
  * - 🗃️ Archive
    - ``.texarr``
    - ``.zip``
  * - ⛰️ Region
    - ``.mdat``
    - ``.mca``
  * - 📄 Document
    - | ``.map`` (launcher), ``itemnames.dat``, ``common``, ``prefs``,
      | ``sd0``, ``sd1``, ``sd2``, ``sd3``, ``sd4``
    - ``.json``

Read more about formats and their support in :doc:`Formats <../formats>`.


----------------------------------------
Model data
----------------------------------------

| A model file can contain geometry, a skeleton, and embedded animation clips.
| These parts are optional and depend on the source file.

Geometry is always parsed. However, it may be absent from the source file, for example in ``.mcvd`` files with first-person animations.
The export then completes with an empty file.

The ``--skeleton`` and ``--animation`` flags enable parsing and exporting the skeleton and animations.
They are exported only when present in the source file.

The skeleton is created for the game engine and may need further work in a 3D editor.

Embedded animations are quite rare. They are usually found in animated decorations (e.g. doors) or mobs (e.g. mutants).
Almost all animations related to the player or NPCs require several linked files.
Use :doc:`Animation <animate>` for these tasks.


----------------------------------------
Output
----------------------------------------

Without a save path, each exported file is saved next to its source file.

When a path is specified, it becomes the root of the export folder. Its structure can be configured.

.. _convert-output-layout:

Output structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Examples of result changes depending on the ``--layout`` option.

.. code-block:: text
  :caption: Source structure

  assets/
  ├── armor/albatros.mcsb
  └── items/vodka.ol


``rooted`` (default)
  Repeats the relative path with the root at the beginning.

  .. code-block:: bash

    scfile convert "./assets" --output "./output"

  .. code-block:: text
    :caption: Output

    output/
    ├── assets/armor/albatros.obj
    └── assets/items/vodka.dds


``relative``
  Repeats the relative path without the root at the beginning.

  .. code-block:: bash

    scfile convert "./assets" --output "./output" --layout relative

  .. code-block:: text
    :caption: Output

    output/
    ├── armor/albatros.obj
    └── items/vodka.dds


``dump``
  Places everything in one flat folder without subfolders.

  .. code-block:: bash

    scfile convert "./assets" --output "./output" --layout dump

  .. code-block:: text
    :caption: Output

    output/
    ├── albatros.obj
    └── vodka.dds

Destination conflicts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An output filename conflict means that the file already existed before conversion began.
The ``--on-conflict`` option determines how to resolve the conflict.

- ``replace`` replaces the existing file with a new one.
- ``rename`` creates a new file with a counter in its name.
- ``skip`` does not create a new file and leaves the existing one unchanged.

Destination collisions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An output filename collision is when several sources claim the same path.
They can occur often with ``--layout dump`` and sometimes with ``--layout relative``.

For a name collision with ``--on-conflict replace``, the first source keeps its original name by default.
The other sources receive a short hash of their source path.
This preserves all files without repeated replacement in a single conversion operation.

Safe replacement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each result is written to a temporary file in the destination folder.
The file at the final path is replaced only after successful conversion.
Therefore, an interrupted conversion does not leave a partially written result.


----------------------------------------
Graphical interface
----------------------------------------

Add files or folders to Sources.
You can also drag and drop them into the drop zone or paste them with ``Ctrl+V``.

Format cards select which source groups to convert.
In the models group, you can select the required format and options for the skeleton and embedded animations.

Results can be saved next to source files or to a specified save path.

For output file name conflicts, you can choose a suitable action policy.


----------------------------------------
Command line
----------------------------------------

.. code-block:: console

   scfile convert "C:/assets"
   scfile convert "model.mcsb" --model-format glb --skeleton
   scfile convert "C:/assets" --output "D:/output" --layout relative

:ref:`Full command options → <cli-convert>`
