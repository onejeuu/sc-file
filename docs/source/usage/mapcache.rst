🗺 Map Cache Preview
==================================================

.. include:: ../_links.rst


----------------------------------------
What it does
----------------------------------------

The map cache contains ``.mdat`` terrain-region fragments, usually located at ``runtime/stalcraft/map_cache/5.0``.
Map Cache groups fragments by coordinates and writes Minecraft Anvil region files named ``r.<x>.<z>.mca``.


----------------------------------------
What is exported
----------------------------------------

The output uses Minecraft Java ``1.12.2`` (Anvil_ ``1343``). It writes terrain
block arrays and biomes. Metadata, lighting, block states and entities are not
exported.

.. note::

   Block IDs differ from Minecraft. By default, the `Block Mapping`_ replaces
   selected IDs with approximate Minecraft blocks.

----------------------------------------
Prepare a world
----------------------------------------

Create a separate local Minecraft Java world before the first export.
A superflat world with structures disabled and only air is convenient for map preview.
Leave the world after creating it.

The ``region`` directory inside that world is the output directory:

.. code-block:: text

   .minecraft/saves/<world>/region
   .minecraft/saves/<world>/dimensions/minecraft/overworld/region (on 26.1+)

You can clear existing ``.mca`` files from this directory before the first export.

.. warning::

   | Always leave the world before replacing its regions.
   | Minecraft can overwrite changed region files with its cached chunks.

Existing files with the same ``r.<x>.<z>.mca`` name are replaced with ``.mca.bck`` backups.


----------------------------------------
Convert the cache
----------------------------------------

In the graphical interface, select the map-cache directory and the target
world or its ``region`` directory. The path resolver changes a selected world
directory to its ``region`` directory automatically (If enabled).

From the command line:

.. code-block:: console

   scfile mapcache "C:/EXBO/runtime/stalcraft/map_cache/5.0" --output ".minecraft/saves/MapPreview/region"

For command options see :ref:`mapcache-cli`.


----------------------------------------
Find the exported regions
----------------------------------------

One ``r.<rx>.<rz>.mca`` file covers ``32 × 32`` chunks, or ``512 × 512``
blocks. Teleport near its centre:

.. code-block:: text

   x = rx × 512 + 256
   z = rz × 512 + 256

For ``r.-3.5.mca``:

.. code-block:: text

   x = -3 × 512 + 256 = -1280
   z =  5 × 512 + 256 =  2816
   /tp @s -1280 100 2816

Use the `Coordinate Calculator`_ when you want a position without calculating
it manually.


----------------------------------------
Viewing setup
----------------------------------------

Resourcepack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the `Map Cache Resource Packs`_.
The original pack targets Minecraft ``1.6.4``. Updated variants are available
for newer formats.


Mods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following Fabric setup is useful for viewing an exported world:

- Fabric_ and `Fabric API`_ for the mods loader.
- Voxy_ for distant terrain rendering.
- C2ME_ for chunk loading optimisation.
- Axiom_ for map editing.
- Optionally other optimisation mods (like Sodium, Lithium, etc).
