🌀 Animation Export
==================================================

.. include:: ../_links.rst


----------------------------------------
What it does
----------------------------------------

Animation files are exported together with their target ``.mcsb`` models. The
result is a ``.glb`` file containing the model and its applied animation data.

The animation and model can be located in different directories. Their file
names alone do not establish compatibility. Each animation operation uses its
own model relationship.


----------------------------------------
Find related assets
----------------------------------------

The paths below are relative to ``runtime/stalcraft/modassets/assets``.

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

``arms`` applies first-person weapon, item, and hands animations from ``.mcvd``
to ``.mcsb`` models. Models are matched to the animation skeleton by bone name.

The shared hands model is ``highpoly/character_hands.mcsb``. A complete
first-person result normally uses both the matching weapon model and this hands
model. Some animations contain only hands and use this model without a weapon.

An export fails when the selected model has no compatible meshes.

For example:

.. code-block:: console

   scfile animate arms "wpn_fp_akm.mcvd" "akm.mcsb" "hands.mcsb"


----------------------------------------
Face
----------------------------------------

``face`` applies facial ``.mcvd`` animation to a head ``.mcsb`` model by matching
morph channel names. Facial animations are generally compatible with head
models that use the same channels.

For example:

.. code-block:: console

   scfile animate face "shaman.mcvd" "unique_shaman.mcsb"


----------------------------------------
Body
----------------------------------------

``body`` applies skeletal animation clips from ``.mcal`` to an ``.mcsb`` model
by bone index. The animation and model must have the same number of bones.

``--raw`` keeps technical and duplicate clips.

.. note::

   MCAL support remains experimental. The format and practical workflows are
   not yet fully understood. Report any problem or idea for improvement through
   `Issues`_.

For example:

.. code-block:: console

   scfile animate body "pack.mcal" "origin.mcsb"
