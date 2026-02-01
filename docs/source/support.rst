✨ Formats Support
==================================================

.. include:: _links.rst

----------------------------------------
``.mcsa`` / ``.mcsb`` / ``.mcvd``
----------------------------------------

Supported Versions: ``7.0``, ``8.0``, ``10.0``, ``11.0``

.. list-table:: Output Formats
  :header-rows: 1

  * - Suffix
    - Name
    - Skeleton
    - Animation
    - Speed
  * - ``.glb``
    - `glTF Binary <GLTF_>`_
    - ✅
    - ✅
    - 8ms
  * - ``.obj``
    - `Wavefront <OBJ_>`_
    - ➖
    - ➖
    - 170ms
  * - ``.dae``
    - `Collada <DAE_>`_
    - ✅
    - ❌
    - 180ms
  * - ``.ms3d``
    - `MilkShape 3D <MS3D_>`_
    - ✅
    - ❌
    - 1120ms

| **Feature:**
| ✅ Supported
| ❌ Not supported by scfile
| ➖ Not supported by format

| Benchmarks were performed using one of the most complex 3D model.
| Note that average results may vary.

----------------------------------------
``.ol``
----------------------------------------

| Supported Formats: ``DXT1``, ``DXT3``, ``DXT5``, ``RGBA8``, ``BGRA8``, ``DXN_XY``, ``RGBA32F``
| Supported Types: ``Texture``, ``Normalmap``, ``Cubemap``

| Output Format: ``.dds`` (`DirectDraw Surface <DDS_>`_)

.. list-table:: Known Formats
  :header-rows: 1

  * - Encoded
    - Decoded
    - Format
    - Compression
  * - ``#?3VGGGGGGGGGGGG``
    - ``DXT1``
    - ``DXT1``
    - ``BC1``
  * - ``#?3TGGGGGGGGGGGG``
    - ``DXT3``
    - ``DXT3``
    - ``BC2``
  * - ``#?3RGGGGGGGGGGGG``
    - ``DXT5``
    - ``DXT5``
    - ``BC3``
  * - ``#?)8?>GGGGGGGGGG``
    - ``DXN_XY``
    - ``ATI2``
    - ``BC5``
  * - ``5 %&_GGGGGGGGGGG``
    - ``RGBA8``
    - ``R8G8B8A8``
    - ``None``
  * - ``% 5&_GGGGGGGGGGG``
    - ``BGRA8``
    - ``B8G8R8A8``
    - ``None``
  * - ``5 %&TU!GGGGGGGGG``
    - ``RGBA32F``
    - ``R32G32B32A32`` (``DX10``)
    - ``None``

`More about Compression... <S3TC_>`_


----------------------------------------
``.mic``
----------------------------------------

| Format: ``.png`` (`Portable Network Graphics <PNG_>`_)
| Only difference is `file signature <SIG_>`_ *(first 4 bytes)*


----------------------------------------
``.texarr``
----------------------------------------

| Output Format: ``.zip`` (`ZIP <ZIP_>`_)
| Textures Format: ``.dds`` (`DirectDraw Surface <DDS_>`_)


----------------------------------------
``NBT``
----------------------------------------

| Format: `Named Binary Tag <NBT_>`_
| Supported Types: ``RAW``, ``GZIP``, ``ZSTD``
| Supported Files: ``assets/stalker/itemnames.dat``, ``config/prefs``, ``config/%Name%/common``, ``config/%Name%/sd0``, ``config/%Name%/sd1``, ``config/%Name%/sd2``, ``config/%Name%/sd3``, ``config/%Name%/sd4``
| Output Format: ``.json`` (`JavaScript Object Notation <JSON_>`_)