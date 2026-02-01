🚀 Usage
==================================================

.. include:: _links.rst

1. **Easiest Way:**
   Use `Drag & Drop <DND_>`_. Just drag and drop files you want convert onto ``scfile.exe``.
   File paths will automatically be taken as arguments, converted to new format, and saved in same location.

2. **File Associations:**
   You can set ``scfile.exe`` as the default application for opening model and texture files.
   When a file is "opened" this way, it will be automatically converted to new format and saved in same location.

3. **Via Console:**
   ``scfile`` is primarily a `CLI <CLI_>`_. If you're comfortable with the terminal, you'll figure it out fast.
   Check out arguments and options with ``scfile.exe --help``.

   .. code-block:: bash

    Usage: scfile [PATHS]... [OPTIONS]

    Options:
      -O, --output DIRECTORY  Output results directory.
      -F, [obj|glb|dae|ms3d]  Preferred format for models.
      --relative              Preserve directory structure from source in output.
      --parent                Use parent directory as starting point in relative directory.
      --skeleton              Parse armature in models.
      --animation             Parse builtin clips in models.
      --unique                Ensure file saved with unique name, avoiding overwrites.
      --version               Show the version and exit.
      --help                  Show help message and exit.

4. **As Library:**
   Install release build using ``pip install sc-file`` or any other package manager.

   :doc:`More details in API Reference... <api/index>`

   .. code-block:: python
    :caption: Simple code example

    from pathlib import Path
    from scfile import UserOptions, convert

    models = Path("models")
    output = Path("output")
    options = UserOptions(parse_skeleton=True, overwrite=False)

    for path in models.rglob("*.mcsb"):
        convert.mcsb_to_glb(source=path, output=output, options=options)

   This code takes all ``.mcsb`` files from ``models`` directory, converts them to ``.glb``, and dumps into ``output``.


----------------------------------------
Output Model Formats
----------------------------------------

| Specify ``--mdlformat`` / ``-F`` parameter followed by desired format suffix.
| For example: ``-F obj`` or ``-F dae``.

| To specify multiple formats at once, you need to use parameter multiple times.
| For example: ``scfile.exe model.mcsb -F obj -F dae -F ms3d``
| This command will create three files: ``model.obj``, ``model.dae``, ``model.ms3d``.


----------------------------------------
Default Model Formats
----------------------------------------

| Default Behavior (without ``-F`` parameter):
| Uses ``consts.py::DefaultModelFormats.STANDARD``: ``.obj``.


| If ``--skeleton`` or ``--animation`` is specified:
| Uses ``consts.py::DefaultModelFormats.SKELETON``: ``.glb``.

**Two ways to change it:**

1. **Easiest Way:**
   Create a shortcut for the ``scfile.exe``. At end of «Target» field, add desired formats like in examples above.

2. **Modify Source Code:**
   Alternatively, tweak this consts in source code and :doc:`compile yourself <compile>`.


----------------------------------------
Model Skeleton
----------------------------------------

| Specify ``--skeleton`` flag.
| If skeleton has presented, it will be exported.
| Output formats with armature support: ``.glb``, ``.dae``, ``.ms3d``.


----------------------------------------
Model Animation
----------------------------------------

| Specify ``--animation`` flag.
| If skeleton and animation has presented, it will be exported.
| Output formats with animation support: ``.glb``.
| `List of files with built-in clips <ANIMSLIST_>`_ (can be outdated).


----------------------------------------
Path Arguments
----------------------------------------

File and directory paths are accepted. Patterns also work.
Quotes are required when paths include spaces.

You can use full paths:
::
  scfile.exe "C:/foo/model.mcsb"

Or relative paths:
::
  scfile.exe "bar/model.mcsb"

You can specify a directory, only files with supported formats will be processed:
::
  scfile.exe "C:/assets"

You can also use patterns. Each file matching the pattern will be passed as a separate argument:
::
  scfile.exe "C:/assets/*.ol"

You can combine multiple arguments, mixing files, directories, and patterns. However, use this with caution and ensure you understand the implications:
::
  scfile.exe "C:/foo/model.mcsb" "bar/model.mcsb" "C:/assets" "C:/assets/*.ol"


----------------------------------------
Output Directory
----------------------------------------

| As mentioned earlier, you can convert entire directories at once.
| By default, output files saved in same location.

You can specify ``--output`` / ``-O`` parameter to change it.
::
  scfile.exe "C:/game/assets" --output "D:/output"


----------------------------------------
Output Overwriting
----------------------------------------

| To prevent overwriting files, use ``--unique`` flag.
| Duplicates files will be renamed like ``model (2).obj``, ``model (3).obj`` and etc.


----------------------------------------
Output Structure
----------------------------------------

| To preserve source directory structure, use ``--relative`` flag.
| Relative path from path argument will be passed as relative path of base ``--output`` directory.

| To use source root directory as starting point in output, use ``--parent`` flag.

.. code-block:: text
  :caption: Example source structure

  ./assets/
  ├── armor/albatros.mcsb
  └── items/vodka.ol

Default Structure
^^^^^^^^^^^^^^^^^^
.. code-block:: bash

  scfile.exe "./assets" --output "./output"

.. code-block:: text
  :caption: Output

  ./output/
  ├── albatros.obj
  └── vodka.dds

Relative Structure
^^^^^^^^^^^^^^^^^^^
.. code-block:: bash

    scfile.exe "./assets" --output "./output" --relative

.. code-block:: text
  :caption: Output

  ./output/
  ├── armor/albatros.obj
  └── items/vodka.dds

Parent Structure
^^^^^^^^^^^^^^^^^
.. code-block:: bash

    scfile.exe "./assets" --output "./output" --parent

.. code-block:: text
  :caption: Output

  ./output/
  ├── assets/armor/albatros.obj
  └── assets/items/vodka.dds