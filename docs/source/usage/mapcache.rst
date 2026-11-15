⛰️ Map cache
==================================================

.. include:: ../_links.rst

| :ref:`mapcache <cli-mapcache>` merges ``.mdat`` cache files into Minecraft ``.mca`` region files.

| Cache files are named ``reg.<x>.<z>.mdat`` and are stored under ``stalcraft/map_cache/<version>``.
| Output files are named ``r.<x>.<z>.mca``.

:Supported versions: ``5``, ``6``, ``7``.
:Format: Minecraft Java ``1.12.2`` (Anvil ``1343``).
:Exported: Terrain block IDs, metadata, and optional biomes.
:NOT Exported: Custom 3D models, entities, original block geometry, or game lighting.


Block mappings
----------------------------------------

Block mappings define how Stalcraft block IDs are represented in Minecraft.

Stalcraft contains custom shapes, ProBuilder geometry, and materials without Minecraft equivalents.
Recognizable shapes such as fences and ladders are matched where possible.
Other blocks are represented by blocks with a similar material appearance.
This avoids dependencies on specific mod loaders and mod sets.


Builtin mappings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``vanilla`` (default)
   Uses blocks to visually or semantically similar Minecraft blocks.

``resourcepack``
   Uses blocks froms `MapCache ResourcePack`_.

``identity``
   Preserves original block IDs. Useful for debugging and custom mappings.

Builtin mappings can be viewed in the `Block Mappings`_ source directory.
Unmapped IDs are exported as air (``0``).


Custom mappings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Custom mappings let you define your own block replacements in JSON.

.. code-block:: json
   :caption: custom.json

   {
     "35": "35",
     "3500": "1:5",
     "2403": "85:0!",
     "1529": "0"
   }

``"35": "35"``
   Uses Minecraft block ``35`` and keeps original metadata.

``"3500": "1:5"``
   Uses Minecraft block ``1`` with metadata ``5``.

``"2403": "85:0!"``
   | Uses Minecraft block ``85`` with metadata ``0``.
   | Symbol ``!`` prevents non air tile material overrides.

``"1529": "0"``
   Replaces block with air.

Source and target IDs can range from ``0`` to ``4095``.
Target metadata ranges from ``0`` to ``15``.
Mapping keys are only block IDs without metadata.


Mapping Editor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Custom mappings can also be created and edited visually using Mapping Editor.

Download source repository, install `astral-sh/uv <UV_>`_, and configure required paths in the config file or command line options.

.. code-block:: console

   uv run -m tools mappings --run

`Development tools → <https://github.com/onejeuu/sc-file/tree/master/tools#mappings>`_


Mapping layers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each ``--blocks`` adds a mapping layer.
It accepts a builtin mapping, a JSON file, or inline string.
Multiple layers can be combined, including several JSON files.

.. code-block:: console

   scfile mapcache "C:/stalcraft/map_cache/7.0" --blocks "vanilla" --blocks "D:/custom.json"
   scfile mapcache "C:/stalcraft/map_cache/7.0" --blocks "resourcepack" --blocks '{"1529": "1:0!"}'

:ref:`Full command options → <cli-mapcache>`


Tile materials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ProBuilder material IDs are stored separately from block IDs.
Tile material IDs use the same mappings and can override block mappings.

Enabled by default. Use ``--no-tiles`` to disable.


Prepare Minecraft world
----------------------------------------

| Create a new Minecraft world.
| Superflat world without structures and ``Void`` preset is recommended.

.. code-block:: text
   :caption: Region directory

   .minecraft/saves/<world>/region
   .minecraft/saves/<world>/dimensions/minecraft/overworld/region (on 26.1+)

Existing ``.mca`` files can be cleared before export.

| Existing region files are backed up as ``.mca.bck`` by default.
| Use ``--no-backup`` to disable.


Convert cache files
----------------------------------------

.. warning::

   Always leave the world before replacing its regions.


.. code-block:: console

   scfile mapcache "stalcraft/map_cache/7.0" --output ".minecraft/saves/MapPreview/region"
   scfile mapcache "D:/legacy" --version "5" --output ".minecraft/saves/Legacy/region"

:ref:`Full command options → <cli-mapcache>`


Find exported regions
----------------------------------------

One ``r.<x>.<z>.mca`` file covers ``32 × 32`` chunks, or ``512 × 512`` blocks.

.. code-block:: text
   :caption: For example, ``r.4.2.mca`` coordinates

   x = 4 × 512 = 2048
   z = 2 × 512 = 1024

   /tp @s 2048 100 1024

Use the `Coordinate Calculator`_ if necessary.


Minecraft setup
----------------------------------------

Resourcepack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Select ``resourcepack`` mapping and download `MapCache ResourcePack`_.

For other versions, convert the pack with `TexturePack Version Converter`_ or another tool.

Mods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use `Fabric`_ with `Fabric API`_, `Voxy`_ for distant rendering, and `C2ME`_ for chunk loading optimisation.
Optional performance mods include Sodium, Lithium, and others.
