📝 Game Formats
==================================================

.. include:: _links.rst

.. warning::
  Formats specifications are based on **reverse-engineering** and may contain inaccuracies.


----------------------------------------
🧊 Model Formats
----------------------------------------

``.mcsa`` Scene Assets (MCSA.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Configuration: Flags, Scales.
| Geometry: Name, Material, Vertex positions, UV1, UV2, Normals, Tangents, Polygons.
| Optional: Skeleton bones, Animation clips.

``.mcsb`` Scene Bundle (MCSA.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Same structure as ``.mcsa`` with leading bytes prefix (?).

``.mcvd`` Vector Dynamic (MCSA.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Identical to ``.mcsa``.
| Used for low-poly geometry with animations (?).

``.mcal`` Animation Library (MCAL.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Character animation clips.
| Used for retargeting animations between compatible armatures.

``.efkmodel`` Effekseer Model (EFKMODEL.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Geometry: Vertex positions, Normals, UV1, Polygons.


----------------------------------------
🧱 Texture Formats
----------------------------------------

``.ol`` Object Layer (OL.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Standard ``.dds`` (`DirectDraw Surface <DDS_>`_) with simplified structure.
| Mipmaps compressed with `LZ4`_.
| Some normal map textures are inverted.

| Cubemap variant exists (OLCUBEMAP.bt_)
| Mostly found in: ``gloomycore/sky``, ``effects/textures``, ``stalker/gui``.

.. list-table:: Texture Suffix Conventions
  :header-rows: 1

  * - Suffix
    - Map
    - Type
    - Purpose
  * - ``_diff``
    - Diffuse
    - Base Color
    - Raw surface color without lighting or reflections.
  * - ``_spek``
    - Specular
    - Reflectivity Control
    - Intensity and sharpness of highlights.
  * - ``_nrm``
    - Normal
    - Surface Detail
    - Simulates bumps and dents without changing geometry.
  * - ``_emi``
    - Emission
    - Self Illumination
    - Makes parts glow or emit light independently.


----------------------------------------
🖼️ Image Formats
----------------------------------------

``.mic`` Media Image Container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Standard ``.png`` (`Portable Network Graphics <PNG_>`_) with modified file signature.
| Previously used for game GUI.


----------------------------------------
🗃️ TextureArray Formats
----------------------------------------

``.texarr`` Texture Array (TEXARR.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Container for ``.dds`` textures.
| Textures referenced as ``group:path`` (e.g., ``probuilder:general/generic``).


----------------------------------------
🗺 Region Formats
----------------------------------------

``.mdat`` World Chunks Cache
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Based on ``.mca`` (`Minecraft Chunks Anvil <ANVIL_>`_) with extended world data.
| Terrain chunks with blocks, metadata, lighting arrays and extra data.
| Chunk data compressed with `ZSTD`_.
| Format is not fully documented.


----------------------------------------
⚙️ NBT Formats
----------------------------------------

| **NBT** (`Named Binary Tag <NBT_>`_) format, viewable with tools like `NBT Explorer <NBTE_>`_.
| In game assets used `GZIP`_ or `ZSTD`_ compression.

Assets
^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
  :header-rows: 1

  * - Filename
    - Compression
    - Purpose
  * - ``stalker/itemnames.dat``
    - ``GZIP``
    - Quest item descriptions.

Configs
^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
  :header-rows: 1

  * - Filename
    - Compression
    - Purpose
    - Keys (examples)
  * - ``prefs``
    - ``ZSTD``
    - UI read state cache.
    - ``seenArticleLinks[], seenExperiences[], hasSeen*``

Per-Character Configs
^^^^^^^^^^^^^^^^^^^^^^

| Located in ``/config/%CharacterName%/``.
| Files prefixed with ``sd`` (**Synced Data**) contain synchronized player state cached locally.

.. list-table::
  :header-rows: 1

  * - Filename
    - Compression
    - Purpose
    - Keys (examples)
  * - ``common``
    - ``ZSTD``
    - General settings and UI states.
    - ``trashedItems[], caseLastOpenCount[], complaintsData{...}, seenFrontlineIntros``
  * - ``sd0``
    - ``ZSTD``
    - Incoming friend requests.
    - ``requests[]``
  * - ``sd1``
    - ``ZSTD``
    - Recent interactions (last 200 players).
    - ``interacts[{allianceId, type, username}]``
  * - ``sd2``
    - ``ZSTD``
    - Notifications history (last 100 popups).
    - ``notifications[{isRead, receivedMoment, notification{...}}]``
  * - ``sd3``
    - ``ZSTD``
    - Donate shop view history.
    - ``observedOffers[]``
  * - ``sd4``
    - ``ZSTD``
    - Profile customization UI state.
    - ``lastSeenBackgroundsVersion, lastSeenPatternsVersion, lastSeenStickersVersion, lastSeenTagsVersion``

Config Formats
^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
  :header-rows: 1

  * - Filename
    - Format
    - Purpose
  * - ``display``
    - Text
    - Selected display ID.
  * - ``keybindings``
    - JSON
    - Keyboard control mappings.
  * - ``options.json``
    - JSON
    - Game settings (graphics, audio, gameplay).
  * - ``quests.json``
    - JSON
    - Quest visibility toggles.
  * - ``waypoints.cfg``
    - JSON
    - Custom map markers.


----------------------------------------
Other Formats
----------------------------------------

``.xeon`` Encrypted Object Notation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Sensitive client data bundle. `AES Encrypted <AES_>`_.
| Mirrors the assets folder structure.

``.mcws`` World Slice
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Chunk of a safezone. `AES Encrypted <AES_>`_.
| Exact purpose is unknown.


----------------------------------------
Launcher Formats
----------------------------------------

``.map`` Hash Mappings (HASHMAP.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Hash Mapping (SHA-1) for game files.
| Used by launcher to verify game assets integrity.

``.torrent.bin`` Torrent Binary (TORRENT.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Modified ``.torrent`` (`Torrent <TORRENT_>`_) file.
| Used by launcher for content delivery.
| Trackers block unauthorized access (token required).
