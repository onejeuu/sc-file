Formats Support
==================================================

----------------------------------------
``.mcsa`` / ``.mcsb`` / ``.mcvd``
----------------------------------------

Supported Versions: ``7.0``, ``8.0``, ``10.0``, ``11.0``

.. list-table:: Output Formats
  :header-rows: 1

  * - Suffix
    - Name
    - Skeleton
    - Animations
  * - ``.obj``
    - `Wavefront <https://en.wikipedia.org/wiki/Wavefront_.obj_file>`_
    - ➖
    - ➖
  * - ``.glb``
    - `glTF Binary <https://en.wikipedia.org/wiki/GlTF>`_
    - ✅
    - ✅
  * - ``.dae``
    - `Collada <https://en.wikipedia.org/wiki/COLLADA>`_
    - ✅
    - ❌
  * - ``.ms3d``
    - `MilkShape 3D <https://developer.valvesoftware.com/wiki/MilkShape_3D>`_
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

Output Format: ``.dds`` (`DirectDraw Surface <https://en.wikipedia.org/wiki/DirectDraw_Surface>`_)

**Recommended Viewers:**
  - `XnView <https://xnview.com>`_ (Versatile)
  - `WTV <https://www.softpedia.com/get/Multimedia/Graphic/Graphic-Viewers/WTV.shtml>`_ (Lightweight)
  - `RenderDoc <https://renderdoc.org/builds>`_ (Analysis)

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

`More about Compression... <https://en.wikipedia.org/wiki/S3_Texture_Compression>`_


----------------------------------------
``.mic``
----------------------------------------

| Absolutely identical to ``.png`` (`Portable Network Graphics <https://en.wikipedia.org/wiki/PNG>`_).
| Only difference is `file signature <https://en.wikipedia.org/wiki/List_of_file_signatures>`_ *(first 4 bytes)*.
