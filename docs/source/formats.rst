Game Formats
==================================================

.. _MCSA.bt: https://github.com/onejeuu/sc-file/blob/master/templates/MCSA.bt
.. _MCAL.bt: https://github.com/onejeuu/sc-file/blob/master/templates/MCAL.bt
.. _OL.bt: https://github.com/onejeuu/sc-file/blob/master/templates/OL.bt
.. _TEXARR.bt: https://github.com/onejeuu/sc-file/blob/master/templates/TEXARR.bt

.. _AES: https://en.wikipedia.org/wiki/Advanced_Encryption_Standard

.. _DDS: https://en.wikipedia.org/wiki/DirectDraw_Surface
.. _PNG: https://en.wikipedia.org/wiki/PNG
.. _JSON: https://en.wikipedia.org/wiki/JSON

.. _MIPMAP: https://en.wikipedia.org/wiki/Mipmap
.. _LZ4: https://en.wikipedia.org/wiki/LZ4_(compression_algorithm)
.. _NORMALMAP: https://en.wikipedia.org/wiki/Normal_mapping
.. _CUBEMAP: https://en.wikipedia.org/wiki/Cube_mapping

.. _SIGNATURE: https://en.wikipedia.org/wiki/List_of_file_signatures
.. _GUI: https://en.wikipedia.org/wiki/Graphical_user_interface

.. warning::
  Formats specifications are based on **reverse-engineering efforts** and may contain inaccuracies.
  Subject to change.

----------------------------------------
Model Formats
----------------------------------------

.. list-table::
  :header-rows: 0

  * - ``.mcsa``
    - **Scene Assets** [`MCSA.bt`_]
       • Configuration: Flags, Scales.
       • Geometry: Name, Material, Vertex Position, UVs, Normals, Polygons.
       • Optional: Skeleton bones, Animation clips.
  * - ``.mcsb``
    - **Scene Bundle** [`MCSA.bt`_]
       • Identical to ``.mcsa`` but with integrity check.
       • Contains leading hash to prevent tampering.
  * - ``.mcvd``
    - **Vector Dynamic** (Collision Mesh) [`MCSA.bt`_]
       • Simplified low-poly geometry.
       • Often includes animation data.
       • Used for physics/collision **trace** detection.
  * - ``.mcal``
    - **Animation Library** [`MCAL.bt`_]
       • Metadata: frame count, bone count.
       • Technical skeletal animation transforms (per bone).
       • Model-specific (requires matching skeleton).
  * - ``.mcws``
    - **World Slice** (`AES Encrypted <AES_>`_)
       • Slices of safezone (world as 3D model).
       • Used in safezone workbench rendering.
       • Aliases: "World Settlement", "Workbench Safezone".


----------------------------------------
Texture Formats
----------------------------------------

``.ol`` (Object Layer) [OL.bt_]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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


``.mic`` (Media Image Container)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Standard ``.png`` (`Portable Network Graphics <PNG_>`_).
| Has modified `file signature <SIGNATURE_>`_.
| Previously used for game `GUI`_.


----------------------------------------
Other
----------------------------------------

``.texarr`` (TEXture ARRay) [TEXARR.bt_]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Container for ``.dds`` (`DirectDraw Surface <DDS_>`_) textures.
| Textures referenced as ``group:path`` (e.g., ``probuilder:general/generic``).


``.xeon`` (eXtended Encrypted Object Notation)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| `AES Encrypted <AES_>`_.
| Contains large `JSON`_ structure.
| Once encrypted individually ``.eon`` files combined into bundles.
