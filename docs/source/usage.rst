🚀 Usage
==================================================

.. include:: _links.rst


----------------------------------------
Quick Start
----------------------------------------

🖥️ **GUI**
  Launch ``scfile.exe`` without arguments to open the graphical interface.
  Add files or folders, choose output formats and settings, and press **Convert**.


📥 **Drag & Drop**
  Drag files or folders directly onto ``scfile.exe`` in File Explorer.
  Supported files are converted to default formats and saved alongside source file.

  This is equivalent to running ``scfile.exe <path>`` for each dropped file.


🖱️ **Open With**
  Set ``scfile.exe`` as the default program for opening supported file types.
  Double-clicking any such file in Explorer will convert it and save output alongside source file.

  To set up: right-click a file → **Open With** → choose ``scfile.exe``
  and check «Always use this app».


📟 **Command Line**
  Run ``scfile.exe --help`` to see all available arguments and options.
  The CLI gives full control over conversion: output formats, skeletons,
  animations, directory structure, file name conflicts, and more.

  .. code-block:: bash

    scfile.exe model.mcsb -F glb --skeleton


📖 **Python Library**
  Install the package from PyPI: ``pip install sc-file -U``.
  Use ``scfile`` directly in your Python scripts, automate complex workflows,
  or build your own tools on top of it.

  :doc:`Full API Reference <api/index>`

  .. code-block:: python
    :caption: Example

    from scfile import Options, convert

    convert.mcsb_to_glb(
        "model.mcsb",
        options=Options(skeleton=True, on_conflict="skip"),
    )


----------------------------------------
Command Line Interface
----------------------------------------

General
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``--version``
    Show the program version and exit.

    .. code-block:: bash

      scfile --version


``--updates``
    Check for available updates on GitHub Releases and exit.
    Requires internet connection.

    .. code-block:: bash

      scfile --updates


convert
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default command. Converts game assets to standard formats.

``PATHS``
  One or more files or directories. Accepts full paths, relative paths,
  and wildcard patterns (``*``). Only files with supported extensions are processed.

  .. code-block:: bash
    :caption: Example

    scfile "model.mcsb"
    scfile "C:/assets"
    scfile "C:/assets/*.ol"
    scfile "model.mcsb" "texture.ol" "C:/assets/*.ol"


``-O, --output``
  Output directory for converted files. If not specified, output files are saved alongside source file.

  .. code-block:: bash
    :caption: Example

    scfile "model.mcsb" --output "D:/output"


``-F, --mdlformat``
  | Preferred output format for models. Repeatable to specify multiple formats.
  | Accepted values: ``obj``, ``glb``, ``fbx``, ``dae``, ``ms3d``.

  | Default is ``obj``.
  | When ``--skeleton`` or ``--animation`` is used, default is ``glb``.

  .. code-block:: bash
    :caption: Example

    scfile "model.mcsb" -F glb
    scfile "model.mcsb" -F glb -F obj -F dae


``--skeleton``
  | Parse and export skeleton (armature) from models.
  | Supported by: ``glb``, ``dae``, ``ms3d``.

  .. code-block:: bash
    :caption: Example

    scfile "model.mcsb" --skeleton
    scfile "model.mcsb" -F glb --skeleton
    scfile "model.mcsb" -F dae --skeleton


``--animation``
  | Parse and export built-in animation clips from models. Implies ``--skeleton``.
  | Supported by: ``glb``.

  .. code-block:: bash
    :caption: Example

    scfile "model.mcsb" --animation
    scfile "model.mcsb" -F glb --animation


``--on-conflict``
  | What to do when an output file already exists.
  | Accepted values: ``overwrite``, ``skip``, ``rename``.
  | Default is ``overwrite``.

  - ``overwrite`` Replace existing file.
  - ``skip`` Keep existing file.
  - ``rename`` Add numeric suffix: ``model (1).obj``, ``model (2).obj``.

  .. code-block:: bash
    :caption: Example

    scfile "C:/assets/model.mcsb" "C:/assets/sub/model.mcsb" --on-conflict rename


``--relative``
  Preserve directory structure of source files inside output directory.
  Requires ``--output``.

  .. code-block:: bash
    :caption: Example

    scfile "C:/assets" --output "D:/output" --relative


``--parent``
  Use parent directory of each source path as root for relative output.
  Implies ``--relative``.

  .. code-block:: bash
    :caption: Example

    scfile "C:/assets" --output "D:/output" --parent


Output Structure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Examples of how ``--relative`` and ``--parent`` change output layout.

.. code-block:: text
  :caption: Source structure

  ./assets/
  ├── armor/albatros.mcsb
  └── items/vodka.ol


Default
  .. code-block:: bash

    scfile "./assets" --output "./output"

  .. code-block:: text
    :caption: Output

    ./output/
    ├── albatros.obj
    └── vodka.dds


``--relative``
  .. code-block:: bash

    scfile "./assets" --output "./output" --relative

  .. code-block:: text
    :caption: Output

    ./output/
    ├── armor/albatros.obj
    └── items/vodka.dds


``--parent``
  .. code-block:: bash

    scfile "./assets" --output "./output" --parent

  .. code-block:: text
    :caption: Output

    ./output/
    ├── assets/armor/albatros.obj
    └── assets/items/vodka.dds


mapcache
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Merges ``.mdat`` cached regions into ``.mca`` region files.
| Run with explicit command or use a path containing ``map_cache`` to auto-detect.

``SOURCE``
  Directory containing ``.mdat`` files.

  .. code-block:: bash
    :caption: Example

    scfile "C:/map_cache/5.0"
    scfile mapcache "C:/map_cache/5.0"


``-O, --output``
  Output directory for ``.mca`` files.
  If not specified, creates a folder alongside ``SOURCE`` with ``_mca`` suffix.

  .. code-block:: bash
    :caption: Example

    scfile mapcache "C:/map_cache/5.0" --output "D:/output"


``-W, --workers``
  | Number of worker threads. Default: ``CPU count × 2``.
  | Set to ``0`` for sequential execution (no threads).

  .. code-block:: bash
    :caption: Example

    scfile mapcache "C:/map_cache/5.0" -W 4


``--raw``
  Keep original block IDs without lookup table replacement.

  .. code-block:: bash
    :caption: Example

    scfile mapcache "C:/map_cache/5.0" --raw
