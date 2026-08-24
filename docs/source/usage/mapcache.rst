🗺 Map Cache Preview
==================================================

.. include:: ../_links.rst


| Map cache contains ``.mdat`` world region fragments.
| Usually located at ``stalcraft/map_cache/5.0``.

| Export groups fragments by coordinates ``x`` and ``z`` in filenames.
| Minecraft Anvil region files named ``r.<x>.<z>.mca``.


----------------------------------------
What is exported
----------------------------------------

| **Format:** Minecraft Java ``1.12.2`` (Anvil_ ``1343``).
| **Exported:** Terrain block arrays and biomes.
| **Not exported:** Models, block states, lighting, entities.

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

In graphical interface, select map cache directory and target world.
Paths resolver changes selected world directory to its ``region`` directory automatically (if enabled).

.. code-block:: console
   :caption: From command line

   scfile mapcache "C:/EXBO/runtime/stalcraft/map_cache/5.0" --output ".minecraft/saves/MapPreview/region"

For command options see :ref:`mapcache-cli`.


----------------------------------------
Find the exported regions
----------------------------------------

One ``r.<rx>.<rz>.mca`` file covers ``32 × 32`` chunks, or ``512 × 512`` blocks.

.. code-block:: text
   :caption: For example coordinates for r.-3.5.mca

   x = -3 × 512 = -1536
   z =  5 × 512 =  2560
   /tp @s -1536 100 2560

Use the `Coordinate Calculator`_ if necessary.


----------------------------------------
Viewing setup
----------------------------------------

Resourcepack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the `Map Cache Resource Packs`_.
Original pack targets Minecraft ``1.6.4``.
Updated variants are available for newer formats.


Mods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following Fabric setup is useful for viewing an exported world:

- Fabric_ and `Fabric API`_ for the mods loader.
- Voxy_ for distant terrain rendering.
- C2ME_ for chunk loading optimisation.
- Axiom_ for map editing.
- Optionally other optimisation mods (like Sodium, Lithium, etc).
