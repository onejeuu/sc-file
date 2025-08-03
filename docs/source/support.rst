Formats Support
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
  * - ``.obj``
    - `Wavefront <OBJ_>`_
    - ➖
    - ➖
  * - ``.glb``
    - `glTF Binary <GLTF_>`_
    - ✅
    - ✅
  * - ``.dae``
    - `Collada <DAE_>`_
    - ✅
    - ❌
  * - ``.ms3d``
    - `MilkShape 3D <MS3D_>`_
    - ✅
    - ❌

| **Feature:**
| ✅ Supported
| ❌ Not supported by scfile
| ➖ Not supported by format


----------------------------------------
``.ol``
----------------------------------------

| Supported Formats: ``DXT1``, ``DXT3``, ``DXT5``, ``RGBA8``, ``BGRA8``, ``DXN_XY``, ``RGBA32F``
| Supported Types: ``Texture``, ``Normalmap``, ``Cubemap``

Output Format: ``.dds`` (`DirectDraw Surface <DDS_>`_)

**Recommended Viewers:**
  - `XnView <XNVIEW_>`_ (Universal)
  - `WTV <WTV_>`_ (Lightweight)
  - `RenderDoc <RENDERDOC_>`_ (Analysis)

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

| Absolutely identical to ``.png`` (`Portable Network Graphics <PNG_>`_)
| Only difference is `file signature <SIG_>`_ *(first 4 bytes)*


----------------------------------------
``.texarr``
----------------------------------------

| Output Format: ``.zip`` (`ZIP <ZIP_>`_)
| Textures Format: ``.dds`` (`DirectDraw Surface <DDS_>`_)
