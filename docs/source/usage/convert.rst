🔄 Converter
==================================================

.. include:: ../_links.rst


| :ref:`convert <cli-convert>` converts supported standalone files.
| Several files and folders can be processed in one operation.
| Folders are scanned recursively.


----------------------------------------
Standalone files
----------------------------------------

A standalone file contains enough data for its own output.
The converter does not need a second file to convert it.

.. list-table::
  :header-rows: 1

  * - Type
    - Sources
    - Output
  * - 🧊 Model
    - ``.mcsa``, ``.mcsb``, ``.mcvd``, ``.efkmodel``
    - ``.obj``, ``.glb``, ``.fbx``
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
    - | ``itemnames.dat``, ``.lang``, ``.sign``, ``.map`` (launcher),
      | ``common``, ``prefs``, ``sd0``, ``sd1``, ``sd2``, ``sd3``, ``sd4``
    - ``.json``

More details about each format are in :doc:`Formats <../formats>`.


----------------------------------------
Model data
----------------------------------------

A model file may contain geometry, a skeleton, and animation clips.
These parts are optional and depend on the source file.

``--skeleton`` reads the skeleton when it is present in the model file.
It does not create a new rig or make the skeleton easier to edit.
The exported skeleton is engine data and may need additional work in a 3D editor.

``--animation`` reads clips embedded in the same model file.
It does not search for animation files or create clips.
The flag does not mean that the model contains animation data.

Some prop and mutant animations are stored in model files.
Most first-person, character, and head animations use separate files and related models.
Use :doc:`Animation <animate>` for these workflows.


----------------------------------------
Output
----------------------------------------

Without an output directory, each result is saved next to its source file.

With an output directory, the output structure controls how source folders are placed inside it.

.. _convert-output-layout:

Output Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Examples of how the output structure changes the result.

.. code-block:: text
  :caption: Source structure

  ./assets/
  ├── armor/albatros.mcsb
  └── items/vodka.ol


``rooted`` (default)
  .. code-block:: bash

    scfile convert "./assets" --output "./output"

  .. code-block:: text
    :caption: Output

    ./output/
    ├── assets/armor/albatros.obj
    └── assets/items/vodka.dds


``relative``
  .. code-block:: bash

    scfile convert "./assets" --output "./output" --layout relative

  .. code-block:: text
    :caption: Output

    ./output/
    ├── armor/albatros.obj
    └── items/vodka.dds


``dump``
  .. code-block:: bash

    scfile convert "./assets" --output "./output" --layout dump

  .. code-block:: text
    :caption: Output

    ./output/
    ├── albatros.obj
    └── vodka.dds


----------------------------------------
Name conflicts and collisions
----------------------------------------

A name conflict means that the destination file already exists before conversion starts.
The conflict policy decides whether to replace, rename, or skip that file.

A collision is different.
It means that several source files resolve to the same destination path during one operation.

Collisions are common with ``dump`` and with several source folders using ``relative``.
For example, two different ``models/weapon.mcsb`` files can both resolve to ``output/weapon.obj``.

With the default ``replace`` policy, the first source keeps the clean name.
The other sources receive a short hash of their source path:

.. code-block:: text

  output/
  ├── weapon.obj
  └── weapon~<hash>.obj

This keeps the results from different sources instead of silently replacing one with another.

``rename`` uses numbered names when a destination is already used.
``skip`` omits a result when its destination is already used.


----------------------------------------
Safe replacement
----------------------------------------

Each result is written to a temporary file in the destination folder.
The final path is replaced only after conversion succeeds.
An interrupted conversion therefore does not leave a partially written result at the final path.


----------------------------------------
Graphical interface
----------------------------------------

Add files and folders to **Sources**.
The source list also accepts drag and drop.

Format cards select which source groups are processed.
The model card selects the model output format.
Skeleton and animation options are available only for formats that support them.

In **Output**, choose whether to save results alongside each source or in a selected folder.
The structure selector is used with a selected folder.

**On Name Collision** selects the action for an existing destination file.


----------------------------------------
Command line
----------------------------------------

.. code-block:: console

   scfile convert "C:/assets"
   scfile convert "model.mcsb" --model-format glb --skeleton
   scfile convert "C:/assets" --output "D:/output" --layout relative

:ref:`Command options → <cli-convert>`
