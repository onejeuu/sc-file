🗺️ 2D Map
==================================================

.. include:: ../_links.rst

:ref:`maptiles <cli-maptiles>` combines map tiles into a single image.
Tiles are placed by the coordinates in their filenames, ``r.<x>.<z>.ol``.


Sources
----------------------------------------

Game installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the game installation when you want a complete map.
Map assets are stored under ``assets/pda/<map>``
and may also be present in ``_localized`` or ``patchassets`` folders.

By default ``--region`` uses system language.

.. code-block:: console
   :caption: Game installation

   scfile maptiles "C:/Steam/steamapps/common/STALCRAFT" "global_map" "D:/maps/global.jpg" --region "ru"

:ref:`Full command options → <cli-maptiles>`


Folder of tiles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use flat folder with all ``.ol`` tiles needed.

.. code-block:: text
   :caption: Tile folder

   tiles/
   ├── r.0.0.ol
   ├── r.0.1.ol
   └── r.1.0.ol

.. code-block:: console
   :caption: Folder of tiles

   scfile maptiles "D:/tiles" "D:/maps/area.png"

:ref:`Full command options → <cli-maptiles>`


Output format
----------------------------------------

**JPEG (default)**

``.jpg`` or ``.jpeg``. Lossy compression. Quality ranges from ``0`` to ``100``
(default ``92``). Higher values retain more detail but increase file size.

**PNG**

``.png``. Lossless. Compression ranges from ``0`` to ``9`` (default ``6``).
Higher compression takes longer and can reduce file size without changing
image quality.

.. code-block:: console

   scfile maptiles "D:/tiles" "D:/maps/area.jpg" --jpeg-quality "95"
   scfile maptiles "D:/tiles" "D:/maps/area.png" --png-compression "9"

:ref:`Full command options → <cli-maptiles>`


Tile handling
----------------------------------------

Tiles with the same proportions can have different pixel resolutions.
Larger tiles are scaled down to the resolution of the smallest one.
Tiles with different aspect ratios cannot be combined.

Files smaller than ``7 KB`` are skipped because they are generally obsolete map tiles.

.. note::

   The full map is assembled in memory before it is saved.
   Large exports can use more than ``1 GB`` of RAM.
