🗺️ 2D Map
==================================================

.. include:: ../_links.rst


| :ref:`maptiles <cli-maptiles>` assembles flat ``r.<x>.<z>.ol`` tiles into one image.
| The result is a 2D map at the scale of the source tiles.


----------------------------------------
Source
----------------------------------------

Flat folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specify a folder with map tiles directly inside it.
Use this mode when the tiles were copied from the game beforehand.

Game folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specify the game assets to choose a region and map.
Map tiles from all asset layers are combined in the order the game loads them.


----------------------------------------
Image format
----------------------------------------

JPEG
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

JPEG is default output format:
its smaller file size and faster encoding matter most for baseline use,
at the cost of lossy compression.

Default quality is ``92``.

PNG
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PNG is lossless alternative:
every pixel is preserved, but files are much larger.

| Default compression level is ``6``.
| Higher levels can take substantially longer.


----------------------------------------
Limits
----------------------------------------

Files smaller than ``7 KB`` are ignored to exclude obsolete game tiles.

Tiles with the same aspect ratio may have different resolutions.
Larger tiles are reduced to the smallest size.
A different aspect ratio stops the export.

The assembled RGB image is held in memory before writing.
Large maps need substantial free RAM, often over ``1 GB`` with temporary images and encoding.


----------------------------------------
Command line
----------------------------------------

.. code-block:: console

   scfile maptiles "D:/tiles" "D:/exports/zone.jpg" --jpeg-quality 95
   scfile maptiles "C:/Steam/steamapps/common/STALCRAFT" map "D:/exports/zone.png" --region ru --png-compression 9

:ref:`Other options → <cli-maptiles>`
