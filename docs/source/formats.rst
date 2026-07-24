📝 Game Formats
==================================================

.. include:: _links.rst

.. warning::
  Formats specifications are based on **reverse-engineering** and may contain inaccuracies.

| Binary templates for `010 Editor`_ are available in the `templates`_ directory.


----------------------------------------
🧊 Model Formats
----------------------------------------

``.mcsa`` Scene Assets (MCSA.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Geometry: Positions, UVs, Normals, Tangents, Vertex colors, Polygons.
| Optional: Skeleton, Animations, Blend shapes.

``.mcsb`` Scene Bundle (MCSA.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Same structure as ``.mcsa``.
| Contains a length-prefixed hash before the signature.

``.mcvd`` Vector Dynamic (MCSA.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Same structure as ``.mcsa``.
| Used for collision models and standalone animation sets.

``.mcal`` Animation Library (MCAL.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Reusable skeletal animation clips stored separately from models.
| Applied to models with matching skeletons.

``.efkmodel`` Effekseer Model (EFKMODEL.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Standard `Effekseer <EFFEKSEER_>`_ model resource used as particle geometry.
| Geometry: Positions, Normals, Binormals, Tangents, UVs, Vertex colors, Polygons.


----------------------------------------
🧱 Texture Formats
----------------------------------------

``.ol`` Object Layer (OL.bt_)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| `GPU texture data <KHRONOS_DATA_FORMAT_>`_ compatible with ``.dds`` (`DirectDraw Surface <DDS_>`_).
| `Mipmaps <MIPMAP_>`_ compressed with `LZ4`_.
| Texture kinds: Default (2D), Cubemap.
| Metadata: Path hash.
| Normal map textures may be inverted.

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

| ``.png`` (`Portable Network Graphics <PNG_>`_) image with an ``MIC`` file signature.
| Primarily used for GUI atlases and composed images.


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

``.mdat`` World Region Cache
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Region container for 32×32 terrain chunks, based on ``.mca`` (`Minecraft Chunks Anvil <ANVIL_>`_).
| Uses 4 KiB sectors with allocation and UUID metadata for each chunk.
| Chunk data includes blocks, metadata, lighting and extended data compressed with `ZSTD`_.


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

| `AES-encrypted <AES_>`_ world slice used to render scene in settlement progression screens.
| Loaded as a separate local world with its own renderer and camera.


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
