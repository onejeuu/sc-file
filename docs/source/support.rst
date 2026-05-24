✨ Formats Support
==================================================

.. include:: _links.rst

----------------------------------------
🧊 Model Formats
----------------------------------------

``.mcsb`` ``.mcsa`` ``.mcvd``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Supported versions: ``7.0``, ``8.0``, ``9.0``, ``10.0``, ``11.0``, ``12.0``

.. list-table::
  :header-rows: 1

  * - Suffix
    - Name
    - Skeleton
    - Animation
    - Time
  * - ``.obj``
    - `Wavefront <OBJ_>`_
    - ➖
    - ➖
    - ``200ms``
  * - ``.glb``
    - `glTF Binary <GLTF_>`_
    - ✅
    - ✅
    - ``20ms``
  * - ``.dae``
    - `Collada <DAE_>`_
    - ✅
    - ❌
    - ``200ms``
  * - ``.ms3d``
    - `MilkShape3D <MS3D_>`_
    - ✅
    - ❌
    - ``1300ms``
  * - ``.fbx``
    - `Autodesk Filmbox <FBX_>`_
    - ❌
    - ❌
    - ``70ms``

| ``✅ Supported``
| ``❌ Not supported by scfile``
| ``➖ Not supported by format``

| Encoding time benchmarked on a complex model. Average results may vary.

``.efkmodel``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Supported versions: ``5``
| Output: ``.obj``, ``.glb``, ``.dae``, ``.ms3d``, ``.fbx``


----------------------------------------
🧱 Texture Formats
----------------------------------------

``.ol``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Output: ``.dds`` (`DirectDraw Surface <DDS_>`_)
| Supported types: ``Texture``, ``Normalmap``, ``Cubemap``

.. list-table::
  :header-rows: 1

  * - Encoded
    - Decoded
    - Format
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


----------------------------------------
🖼️ Image Formats
----------------------------------------

``.mic``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Output: ``.png`` (`Portable Network Graphics <PNG_>`_)
| Only difference from standard PNG is the file signature.


----------------------------------------
📦 TextureArray Formats
----------------------------------------

``.texarr``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Output: ``.zip`` (`ZIP <ZIP_>`_)
| Contains ``.dds`` textures.


----------------------------------------
🗺 Region Formats
----------------------------------------

``.mdat``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Output: ``.mca`` (`Anvil <ANVIL_>`_). Version ``1343``. Minecraft ``1.12.2``.
| Only basic blocks export.


----------------------------------------
⚙️ NBT Formats
----------------------------------------

| Output: ``.json`` (`JavaScript Object Notation <JSON_>`_)
| Supported types: ``RAW``, ``GZIP``, ``ZSTD``
| Supported files: ``stalker/itemnames.dat``, ``config/prefs``, ``config/%Name%/common``, ``config/%Name%/sd0..4``
