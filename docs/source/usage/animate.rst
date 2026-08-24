🌀 Animation Export
==================================================

.. include:: ../_links.rst


| Animation files are exported together with their target models.
| Result is a ``.glb`` file containing model with applied animation clips.


----------------------------------------
Find related assets
----------------------------------------

| Animation and model usually located in different directories.
| Paths below are relative to ``stalcraft/modassets/assets``.

.. list-table::
  :header-rows: 1

  * - Operation
    - Animation files
    - Target models
    - Mappings
  * - Arms
    - ``highpoly/animations``
    - | ``weapons/models``
      | ``highpoly/character_hands.mcsb``
    - `Arms Mappings`_
  * - Face
    - | ``highpoly/lipsync``
      | ``stalkerplayer/head_animations``
    - | ``stalkerplayer/heads``
      | ``stalkerplayer/arkit``
    - `Face Mappings`_
  * - Body
    - | ``highpoly/character``
      | ``customnpcs``
      | ``customitems``
    - Mapped ``.mcsb`` files
    - `Body Mappings`_

----------------------------------------
Arms
----------------------------------------

| ``arms`` applies first-person weapon, item, and hands animations from ``.mcvd`` clips to ``.mcsb`` models.
| Models are matched to the animation skeleton by bone name.

The shared hands model is ``highpoly/character_hands.mcsb``. A complete
first-person result normally uses both the matching weapon model and this hands
model. Some animations contain only hands and use this model without a weapon.

.. code-block:: console
   :caption: For example

   scfile animate arms "wpn_fp_akm.mcvd" "akm.mcsb" "hands.mcsb"
   scfile animate arms "wpn_fp_akm.mcvd" "akm.mcsb"
   scfile animate arms "wpn_fp_walkcycles.mcvd" "hands.mcsb"


----------------------------------------
Face
----------------------------------------

| ``face`` applies facial ``.mcvd`` clips to a head ``.mcsb`` model.
| Models are matched by morph channel names.

.. code-block:: console
   :caption: For example

   scfile animate face "shaman.mcvd" "unique_shaman.mcsb"


----------------------------------------
Body
----------------------------------------

| ``body`` applies skeletal ``.mcal`` clips to body ``.mcsb`` model.
| Models are matched by bone index.

``--raw`` keeps technical and duplicate clips.

.. note::

   MCAL support remains experimental.
   The format and practical workflows are not yet fully understood.
   Report any problem or idea for improvement in `Issues`_.

.. code-block:: console
   :caption: For example

   scfile animate body "pack.mcal" "origin.mcsb"
   scfile animate body "pack.mcal" "origin.mcsb" --raw
