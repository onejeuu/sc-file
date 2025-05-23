Game Formats
==================================================

.. warning::
  Format specifications are based on **reverse-engineering efforts** and may contain inaccuracies. No claim to credibility.
  This documentation reflects our current understanding and is subject to change.

----------------------------------------
Model Formats
----------------------------------------

.. list-table::
  :header-rows: 0

  * - ``.mcsa``
    - **Scene Assets**
       • Configuration: Flags, Scales.
       • Geometry: Name, Material, Vertex Position, UVs, Normals, Polygons.
       • Optional: Skeleton bones, Animation clips.
  * - ``.mcsb``
    - **Scene Bundle**
       • Identical to ``.mcsa`` but with integrity check.
       • Contains leading hash to prevent tampering.
  * - ``.mcvd``
    - **Vector Dynamic** (Collision Mesh)
       • Simplified low-poly geometry.
       • Often includes animation data.
       • Used for physics/collision **trace** detection.
  * - ``.mcal``
    - **Animation Library**
       • Metadata: frame count, bone count.
       • Technical skeletal animation transforms (per bone).
       • Model-specific (requires matching skeleton).
  * - ``.mcws``
    - **World Slice** (`AES Encrypted <https://en.wikipedia.org/wiki/Advanced_Encryption_Standard>`_)
       • Slices of safezone (world as 3D model).
       • Used in safezone workbench rendering.
       • Aliases: "World Settlement", "Workbench Safezone".


----------------------------------------
Texture Formats
----------------------------------------

``.ol`` (Object Layer)
^^^^^^^^^^^^^^^^^^^^^^^

| Standard ``.dds`` (`DirectDraw Surface <https://en.wikipedia.org/wiki/DirectDraw_Surface>`_).
| Has simplified structure and `mipmaps <https://en.wikipedia.org/wiki/Mipmap>`_ are compressed using `LZ4 <https://en.wikipedia.org/wiki/LZ4_(compression_algorithm)>`_.

| Some `normal maps <https://en.wikipedia.org/wiki/Normal_mapping>`_ textures can be inverted.

| Some textures can be `cube maps <https://en.wikipedia.org/wiki/Cube_mapping>`_.
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

| Standard ``.png`` (`Portable Network Graphics <https://en.wikipedia.org/wiki/PNG>`_).
| Has modified `file signature <https://en.wikipedia.org/wiki/List_of_file_signatures>`_.
| Previously used for game `GUI <https://en.wikipedia.org/wiki/Graphical_user_interface>`_.

----------------------------------------
Other
----------------------------------------

``.xeon`` (eXtended Encrypted Object Notation)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| `AES Encrypted <https://en.wikipedia.org/wiki/Advanced_Encryption_Standard>`_.
| Contains large `JSON <https://en.wikipedia.org/wiki/JSON>`_ structure.
| Once encrypted individually ``.eon`` files combined into bundles.
