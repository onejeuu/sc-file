Index
==================================================

.. include:: _links.rst

.. toctree::
  :maxdepth: 1

  usage
  faq
  support
  formats
  compile

  api/index
  v/index


----------------------------------------
Overview
----------------------------------------

**scfile** is a utility and library for converting proprietary Stalcraft assets formats to standard ones.

  This is an **unofficial** project and is **not affiliated** with EXBO.


.. list-table:: ✨ Supported Formats
  :header-rows: 1

  * - Type
    - Game formats
    - Standard formats
  * - 🧊 **Model**
    - ``.mcsb`` ``.efkmodel``
    - ``.obj`` ``.glb`` ``.dae`` ``.ms3d`` ``.fbx``
  * - 🧱 **Texture**
    - ``.ol``
    - ``.dds``
  * - 🖼️ **Image**
    - ``.mic``
    - ``.png``
  * - 📦 **Archive**
    - ``.texarr``
    - ``.zip``
  * - 🗺 **Region**
    - ``.mdat``
    - ``.mca``
  * - ⚙️ **NBT\***
    - ``...``
    - ``.json``

\* ``NBT`` refers to specific files (``itemnames.dat``, ``prefs``, ``sd0``, etc.)

.. seealso::

  📚 :doc:`Detailed formats support → <support>`


.. important::

  | **Reverse conversion** (``standard`` → ``game``) **is not available.**
  | 📚 :doc:`See FAQ for details → <faq>`


----------------------------------------
🚀 Installation
----------------------------------------

  **Three ways to get started:** download, install, or compile.

💻 Download executable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Standalone ``scfile.exe`` available on `Releases page <https://github.com/onejeuu/sc-file/releases>`_
| *No Python required.*

**Usage:**

- 🖥️ **GUI**: launch `scfile.exe` without arguments to open graphical interface
- 📥 **Drag & Drop**: drag file onto ``scfile.exe``
- 🖱️ **Open With**: set as default app for supported formats
- 📟 **Command Line**: ``scfile.exe --help``
   | *Command example:* ``scfile.exe model.mcsb -F glb --skeleton``
   | *Options in example:* ``-F`` *picks model format,* ``--skeleton`` *extracts model armature.*

🐍 Install Python package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Install:**

.. code-block:: bash

  pip install sc-file


**Usage:**

- 📖 **Python library**: *See Library section*
- 🖥️ **GUI via package**: `scfile`
- 📟 **CLI via package**: ``scfile --help``

🔧 Compile from source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Build from source code using the :doc:`compile guide <compile>`.
| *For developers, contributors, or custom builds.*


----------------------------------------
📖 Library
----------------------------------------

**Install latest version:**

.. code-block:: bash

  pip install sc-file -U


.. code-block:: python
    :caption: Usage example

    from scfile import convert, formats, Options

    # Simple conversion (auto detect format by file suffix)
    # User options to control parsing and export settings
    convert.auto("model.mcsb", options=Options(skeleton=True))

    # Advanced control (manual decoding and data inspection)
    # Context manager ensures proper resource cleanup
    with formats.mcsb.McsbDecoder("model.mcsb") as mcsb:
        # Access parsed scene data: meshes, bones, etc
        data = mcsb.decode()
        print(f"Meshes: {[mesh.name for mesh in data.scene.meshes]}")
        print(f"Materials: {[mesh.material for mesh in data.scene.meshes]}")
        print(f"Bones: {[bone.name for bone in data.scene.skeleton.bones]}")

        # Export to a specific standard format
        mcsb.to_obj().save("output.obj")


.. seealso::

  📚 :doc:`Complete Library API reference → <api/index>`


----------------------------------------
🔗 Links
----------------------------------------

- ``❓`` **Questions?** Check :doc:`FAQ <faq>` or `contact me <TG_>`_
- ``🐛`` **Found a bug?** `Open an issue <ISSUES_>`_
- ``💻`` **Download executable:** `Latest release <RELEASES_>`_
- ``🔧`` **Compile from source:** :doc:`Build guide <compile>`


----------------------------------------
🤝 Acknowledgments
----------------------------------------

| ``kommunist2021`` · ``Art3mLapa`` · ``n1kodim`` · ``TeamDima`` · ``BoJIwEbNuK7``
| ``IExploitableMan`` · ``tuneyadecc`` · ``Hazart``

Thanks to everyone who reported issues, shared findings, or contributed ideas.
