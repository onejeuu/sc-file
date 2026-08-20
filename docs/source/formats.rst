📚 Formats
==================================================

.. include:: _links.rst

.. warning::
  Format specifications are based on **reverse-engineering** and may contain inaccuracies.

| Binary templates for `010 Editor`_ are available in the `templates`_ directory.


----------------------------------------
🧊 Model Formats
----------------------------------------

.. _mcsa:

``.mcsa`` Scene Assets (Legacy)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Template:** MCSA.bt_
| **Purpose:** Model scene.
| **Contents:** Geometry, materials, skeletons, animation clips and blend shapes.
| **Support:** Versions ``7.0``, ``8.0``, ``9.0``, ``10.0``, ``11.0``, ``12.0``, ``15.0``.

.. _mcsb:

``.mcsb`` Scene Bundle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Template:** MCSA.bt_
| **Purpose:** Model scene.
| **Contents:** Hash before the signature.

.. _mcvd-trace:

``.mcvd`` Trace Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Template:** MCSA.bt_
| **Purpose:** Collision and physics geometry.
| **Also:** :ref:`Standalone animation sets <mcvd-animation>` use the same suffix.

.. _efkmodel:

``.efkmodel`` Effekseer Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Template:** EFKMODEL.bt_
| **Purpose:** Effekseer_ animated particle model.
| **Contents:** Frame-based geometry with vertices and triangles. Vertices contain positions, normals, binormals, tangents, UVs and colors.
| **Support:** Version ``5``.

.. _model-export:

Export
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
  :header-rows: 1

  * - Suffix
    - Name
    - UV2
    - Tangents
    - Armature
    - Bone Clips
    - Morph Clips
  * - ``.obj``
    - `Wavefront OBJ <OBJ_>`_
    - ➖
    - ➖
    - ➖
    - ➖
    - ➖
  * - ``.glb``
    - `glTF Binary <GLTF_>`_
    - ✅
    - ✅
    - ✅
    - ✅
    - ✅
  * - ``.fbx``
    - `Autodesk FBX <FBX_>`_
    - ✅
    - ❌
    - ✅
    - ✅
    - ❌

| ``✅ Supported``
| ``❌ Not supported by scfile``
| ``➖ Not supported by format``


----------------------------------------
🌀 Animation Formats
----------------------------------------

.. _mcvd-animation:

``.mcvd`` Animation Set
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Template:** MCSA.bt_
| **Purpose:** Standalone skeletal or facial animation clips.
| **Note:** Usually located in ``assets/highpoly``.

.. _mcal:

``.mcal`` Animation Library
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Template:** MCAL.bt_
| **Purpose:** Shared clips by models with matching skeletons.
| **Contents:** Skeletal animation clips.

Export
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Input:** Animation data and one or more compatible :ref:`.mcsb <mcsb>` model scenes.
| **Output:** :ref:`.glb <model-export>` with the assembled scene.
| **Note:** Relation pairs can be found in `Audit Mappings`_.


----------------------------------------
🧱 Texture Formats
----------------------------------------

``.ol`` Object Layer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Template:** OL.bt_
| **Purpose:** Mipmapped texel data compatible with ``.dds`` (`DirectDraw Surface <DDS_>`_).
| **Contents:** Default 2D textures and cubemaps. Mipmaps use `lz4`_ compression.
| **Export:** ``.dds``.
| **Note:** Normal maps may have an inverted Y axis.

.. list-table:: Suffix Conventions
  :header-rows: 1

  * - Suffix
    - Map
    - Type
    - Purpose
  * - ``_diff``
    - Diffuse
    - Base Color
    - Raw surface color
  * - ``_spek``
    - Specular
    - Reflectivity Control
    - Intensity of highlights
  * - ``_nrm``
    - Normal
    - Surface Detail
    - Simulates bumps and dents
  * - ``_emi``
    - Emission
    - Self Illumination
    - Creates independent glow

.. list-table:: FourCC Formats
  :header-rows: 1

  * - Encoded
    - Game Format
    - DDS Format
    - Compression
  * - ``#?3V``
    - ``DXT1``
    - ``DXT1``
    - ``BC1``
  * - ``#?3T``
    - ``DXT3``
    - ``DXT3``
    - ``BC2``
  * - ``#?3R``
    - ``DXT5``
    - ``DXT5``
    - ``BC3``
  * - ``#?)8?``
    - ``DXN_X``
    - ``ATI1``
    - ``BC4``
  * - ``#?)8?>``
    - ``DXN_XY``
    - ``ATI2``
    - ``BC5``
  * - ``5 %&_``
    - ``RGBA8``
    - ``R8G8B8A8``
    - ``None``
  * - ``% 5&_``
    - ``BGRA8``
    - ``B8G8R8A8``
    - ``None``
  * - ``5 %&TU!``
    - ``RGBA32F``
    - ``R32G32B32A32``
    - ``None``

``.sign`` Texture Signatures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Template:** SIGN.bt_
| **Purpose:** Texture integrity verification.
| **Contents:** Texture paths, headers and mipmap images hashes.


----------------------------------------
🖼️ Image Formats
----------------------------------------

``.mic`` Media Image Container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Purpose:** GUI and composed images.
| **Contents:** ``.png`` (`Portable Network Graphics <PNG_>`_) data with an ``MIC`` signature.
| **Export:** ``.png``.


----------------------------------------
🗃️ Archive Formats
----------------------------------------

.. _texarr:

``.texarr`` Texture Array
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Template:** TEXARR.bt_
| **Purpose:** Container for ``.dds`` (`DirectDraw Surface <DDS_>`_) textures.
| **Export:** ``.zip`` (ZIP_).


----------------------------------------
🗺 Region Formats
----------------------------------------

``.mdat`` World Region Cache
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Purpose:** Region container for 32×32 terrain chunks.
| **Contents:** Blocks, metadata, lighting, biomes and extended data compressed with `zstd`_.
| **Export:** Anvil version ``1343`` for Minecraft ``1.12.2`` with approximate block mapping.
| :doc:`Map Cache viewing guide → <usage/mapcache>`

----------------------------------------
⚙️ NBT Files
----------------------------------------

| **Format:** `Named Binary Tag <NBT_>`_ data.
| **Compression:** None, gzip_, zstd_.
| **Export:** ``.json`` (`JavaScript Object Notation <JSON_>`_).

.. list-table::
  :header-rows: 1

  * - Path
    - Compression
    - Purpose
    - Keys (examples)
  * - ``stalker/itemnames.dat``
    - gzip_
    - Quest item descriptions
    - ➖
  * - ``config/prefs``
    - zstd_
    - UI read state cache
    - ``seenArticleLinks[], seenExperiences[], hasSeen*``
  * - ``config/<Name>/common``
    - zstd_
    - General settings and UI states
    - ``trashedItems[], caseLastOpenCount[], complaintsData{...}, seenFrontlineIntros``
  * - ``config/<Name>/sd0``
    - zstd_
    - Incoming friend requests
    - ``requests[]``
  * - ``config/<Name>/sd1``
    - zstd_
    - Recent interactions (last 200 players)
    - ``interacts[{allianceId, type, username}]``
  * - ``config/<Name>/sd2``
    - zstd_
    - Notifications history (last 100 popups)
    - ``notifications[{isRead, receivedMoment, notification{...}}]``
  * - ``config/<Name>/sd3``
    - zstd_
    - Donate shop view history
    - ``observedOffers[]``
  * - ``config/<Name>/sd4``
    - zstd_
    - Profile customization UI state
    - ``lastSeenBackgroundsVersion, lastSeenPatternsVersion, lastSeenStickersVersion, lastSeenTagsVersion``


----------------------------------------
🛠️ Config Files
----------------------------------------

.. list-table::
  :header-rows: 1

  * - Filename
    - Format
    - Purpose
  * - ``display``
    - ➖
    - Selected display ID
  * - ``keybindings``
    - JSON_
    - Keyboard control mappings
  * - ``options.json``
    - JSON_
    - Game settings (graphics, audio, gameplay)
  * - ``quests.json``
    - JSON_
    - Quest visibility toggles
  * - ``waypoints.cfg``
    - JSON_
    - Custom map markers


----------------------------------------
📄 Text Formats
----------------------------------------

.. list-table::
  :header-rows: 1

  * - Suffix
    - Format
    - Purpose
  * - ``.lang``
    - `Java Properties <PROPERTIES_>`_
    - Localization strings
  * - ``.properties``
    - `Java Properties <PROPERTIES_>`_
    - Configuration
  * - ``.md``
    - Markdown_
    - Formatted text
  * - ``.srt``
    - SubRip_
    - Subtitles
  * - ``.smm``
    - JSON_
    - Mob configuration


----------------------------------------
🔒 Encrypted Formats
----------------------------------------

.. note::

   Used AES_. Decryption requires a key recovered from the protected game client.

``.xeon`` Encrypted Bundle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Purpose:** Bundle with sensitive client data.
| **Contents:** Copy of the assets folder structure.

``.mcws`` World Slice
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Purpose:** Settlement progression screens.
| **Contents:** World slice chunks.

``.ta`` Texture Array
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Purpose:** Protection of high resolution texture array.
| **Contents:** :ref:`.texarr <texarr>` data.

``.bank`` Audio Bank
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Engine:** `FMOD Studio <FMOD_>`_.
| **Purpose:** Primarily voice acting and OST.
| **Contents:** Adaptive audio events.


----------------------------------------
🕹️ Launcher Formats
----------------------------------------

``.map`` Hash Mappings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Template:** HASHMAP.bt_
| **Purpose:** Launcher file integrity verification.
| **Contents:** Game asset paths and SHA-1 hashes.

``.torrent.bin`` Torrent Binary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Template:** TORRENT.bt_
| **Purpose:** Game content delivery.
| **Contents:** Modified ``.torrent`` (Torrent_) data. Trackers require a token.
