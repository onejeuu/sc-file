🚀 Usage
==================================================

.. include:: _links.rst

.. toctree::
  :hidden:

  usage/mapcache
  usage/animate


----------------------------------------
Quick Start
----------------------------------------

🖥️ **GUI**
  Launch ``scfile.exe`` without arguments to open the graphical interface.
  Use **Convert** for standalone assets, **Animation** for model and animation pairs,
  and **Map Cache** for region caches.


📥 **Drag & Drop**
  Drag files or folders directly onto ``scfile.exe`` in File Explorer.
  Supported files are converted to default formats and saved alongside the source file.


🖱️ **Open With**
  Set ``scfile.exe`` as the default program for opening supported file types.
  Double-clicking any such file in Explorer will convert it and save output alongside the source file.

  To set up: right-click a file → **Open With** → choose ``scfile.exe``
  and check **Always use this app**.


📟 **Command Line**
  Run ``scfile.exe --help`` to see all available arguments and options.
  Paths are routed automatically to conversion, animation, or map cache operations.

  .. code-block:: bash

    scfile.exe model.mcsb -F fbx --skeleton # convert to fbx with skeleton
    scfile.exe clips.mcvd model.mcsb # convert animation clips
    scfile.exe path/to/map_cache/5.0 # convert map cache


📖 **Python Library**
  Install the package from PyPI: ``pip install sc-file -U``.
  Use ``scfile`` from your Python scripts.

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

``COMMAND``
  | Available commands: ``convert``, ``animate``, and ``mapcache``.
  | When paths are supplied without a command, the CLI selects one from their names and formats.

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
  One or more files or directories. Accepts absolute and relative paths.
  Only supported files are processed.

  .. code-block:: bash
    :caption: Example

    scfile "model.mcsb" # auto route
    scfile "C:/assets" # auto route
    scfile convert "model.mcsb" "texture.ol" # explicit command


``-O, --output``
  Output directory for converted files. If not specified, output files are saved alongside the source file.

  .. code-block:: bash
    :caption: Example

    scfile convert "model.mcsb" --output "D:/output"


``-F, --model-format``
  | Preferred output format for models.
  | Accepted values: ``obj``, ``glb``, ``fbx``.

  | Default is ``obj``.
  | When ``--skeleton`` or ``--animation`` is used, default is ``glb``.

  .. code-block:: bash
    :caption: Example

    scfile convert "model.mcsb" -F glb


``-I, --include``
  Process only the specified source formats. May be repeated.

  .. code-block:: bash
    :caption: Example

    scfile convert "C:/assets" --include mcsb
    scfile convert "C:/assets" -I mcsb -I ol


``--skeleton``
  | Export model skeleton (armature).
  | Supported by: ``glb``, ``fbx``.

  .. code-block:: bash
    :caption: Example

    scfile convert "model.mcsb" --skeleton
    scfile convert "model.mcsb" -F glb --skeleton
    scfile convert "model.mcsb" -F fbx --skeleton


``--animation``
  | Export embedded animation clips. Implies ``--skeleton``.
  | Supported by: ``glb``, ``fbx``.

  .. code-block:: bash
    :caption: Example

    scfile convert "model.mcsb" --animation
    scfile convert "model.mcsb" -F glb --animation


``--on-conflict``
  | What to do when an output file already exists in output directory.
  | Accepted values: ``overwrite``, ``skip``, ``rename``.
  | Default is ``overwrite``.

  - ``overwrite``: Replace existing file.
  - ``skip``: Keep existing file.
  - ``rename``: Add numeric suffix: ``model (1).obj``, ``model (2).obj``.

  .. code-block:: bash
    :caption: Example

    scfile convert "C:/assets/model.mcsb" "C:/assets/sub/model.mcsb" --on-conflict rename


``--layout``
  | Output layout. Requires ``--output``. Defaults to ``flat``.
  | Accepted values: ``flat``, ``relative``, ``rooted``. `Examples → <layout_>`_

  .. code-block:: bash
    :caption: Example

    scfile convert "C:/assets" --output "D:/output" --layout relative


``-W, --workers``
  | Number of worker threads. Default: CPU count.
  | Set to ``0`` for sequential execution.

  .. code-block:: bash
    :caption: Example

    scfile convert "C:/assets" --workers 4


``-v, --verbose``
  Show the result of every processed file.


.. _layout:

Output Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Examples of how ``--layout`` changes output layout.

.. code-block:: text
  :caption: Source structure

  ./assets/
  ├── armor/albatros.mcsb
  └── items/vodka.ol


``flat`` (default)
  .. code-block:: bash

    scfile convert "./assets" --output "./output"

  .. code-block:: text
    :caption: Output

    ./output/
    ├── albatros.obj
    └── vodka.dds


``relative``
  .. code-block:: bash

    scfile convert "./assets" --output "./output" --layout relative

  .. code-block:: text
    :caption: Output

    ./output/
    ├── armor/albatros.obj
    └── items/vodka.dds


``rooted``
  .. code-block:: bash

    scfile convert "./assets" --output "./output" --layout rooted

  .. code-block:: text
    :caption: Output

    ./output/
    ├── assets/armor/albatros.obj
    └── assets/items/vodka.dds


animate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Applies external animation data to one or more ``.mcsb`` models and exports a ``.glb`` file. Each subcommand accepts ``-O, --output`` for a GLB file or directory. Without it, the GLB is saved next to the animation source.

:doc:`Open the animation export guide → <usage/animate>`

``arms ANIMATION MODEL [HANDS]``
  Apply a first-person ``.mcvd`` animation to a weapon ``.mcsb`` model. Add an optional hands model.

  .. code-block:: bash
    :caption: Example

    scfile animate arms "wpn_fp_ak.mcvd" "ak.mcsb" "hands.mcsb"


``face ANIMATION MODEL``
  Apply a facial ``.mcvd`` animation to a head ``.mcsb`` model.

  .. code-block:: bash
    :caption: Example

    scfile animate face "character.mcvd" "head.mcsb"


``body ANIMATION MODEL``
  Apply an ``.mcal`` skeletal animation library to an ``.mcsb`` model.

  ``--raw``
    Keep technical clips that are normally filtered from the export.

  .. code-block:: bash
    :caption: Example

    scfile animate body "character.mcal" "character.mcsb" --raw


.. _mapcache-cli:

mapcache
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Merges ``.mdat`` region caches into ``.mca`` region files.
| Run with explicit command or use a path containing ``map_cache`` to auto-detect.
| :doc:`Open the Map Cache viewing guide → <usage/mapcache>`

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
  | Number of worker threads. Default: CPU count.
  | Set to ``0`` for sequential execution.

  .. code-block:: bash
    :caption: Example

    scfile mapcache "C:/map_cache/5.0" --workers 4


``--raw``
  Keep original block IDs instead of lookup table replacement.

  .. code-block:: bash
    :caption: Example

    scfile mapcache "C:/map_cache/5.0" --raw


``-v, --verbose``
  Show the result of every processed region.
