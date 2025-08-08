Game Formats
==================================================

.. include:: _links.rst

.. warning::
  Formats specifications are based on **reverse-engineering efforts** and may contain inaccuracies.
  Subject to change.


----------------------------------------
🧊 Model Formats
----------------------------------------

.. list-table::
  :header-rows: 0

  * - ``.mcsa``
    - **Scene Assets** (MCSA.bt_)
       • Configuration: Flags, Scales.
       • Geometry: Name, Material, Vertex Position, UVs, Normals, Polygons.
       • Optional: Skeleton bones, Animation clips.
  * - ``.mcsb``
    - **Scene Bundle** (MCSA.bt_)
       • Identical to ``.mcsa`` but with integrity check.
       • Contains leading hash to prevent tampering.
  * - ``.mcvd``
    - **Vector Dynamic** (MCSA.bt_)
       • Simplified low-poly geometry.
       • Includes animation data.
       • Used for physics/collision trace detection.
  * - ``.mcal``
    - **Animation Library** (MCAL.bt_)
       • Metadata: frame count, bone count.
       • Technical skeletal animation transforms (per bone).
       • Model-specific (requires matching skeleton).
  * - ``.mcws``
    - **World Slice** (`AES Encrypted <AES_>`_)
       • Slices of safezone (world as 3D model).
       • Used in safezone workbench rendering.


----------------------------------------
🧱 Texture Formats
----------------------------------------

``.ol`` Object Layer (OL.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Standard ``.dds`` (`DirectDraw Surface <DDS_>`_).
| Has simplified structure and `mipmaps <MIPMAP_>`_ are compressed using `LZ4`_.

| Some `normal maps <NORMALMAP_>`_ textures can be inverted.

| Some textures can be `cube maps <CUBEMAP_>`_.
| Mainly located in: ``gloomycore/sky``, ``effects/textures``, ``stalker/gui``.

.. list-table:: Texture Suffix Conventions
  :header-rows: 1

  * - Suffix
    - Map
    - Type
    - Purpose
  * - ``_diff``
    - Diffuse
    - Base Color / Albedo
    - Contains raw surface color without lighting or reflections.
  * - ``_spek``
    - Specular
    - Reflectivity Control
    - Defines intensity and sharpness of highlights/reflections.
  * - ``_nrm``
    - Normal
    - Surface Detail
    - Simulates small bumps/dents without changing geometry.
  * - ``_emi``
    - Emission
    - Self-Illumination
    - Makes parts glow or emit light independently.

``.mic`` Media Image Container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Standard ``.png`` (`Portable Network Graphics <PNG_>`_).
| Has modified `file signature <SIG_>`_.
| Previously used for game `GUI`_.

``.texarr`` TEXture ARRay (TEXARR.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Container for ``.dds`` (`DirectDraw Surface <DDS_>`_) textures.
| Textures referenced as ``group:path`` (e.g., ``probuilder:general/generic``).


----------------------------------------
🗂️ Other Formats
----------------------------------------

``.xeon`` eXtended Encrypted Object Notation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Contains large `JSON`_ structure. `AES Encrypted <AES_>`_.
| Once encrypted individually ``.eon`` files combined into bundles.


----------------------------------------
🛠️ Launcher Formats
----------------------------------------

``.map`` MAPping hashes (DIRMAP.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Contains SHA-1 hash mappings for game files.
| Used by launcher for integrity verification.

``.torrent.bin`` TORRENT BINary (TORRENT.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Modified ``.torrent`` (`Torrent <TORRENT_>`_) file.
| Used by game launcher for content delivery.
| Trackers block unauthorized access (token required).
