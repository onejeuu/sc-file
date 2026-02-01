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
    - ``.mcsb`` ``.mcsa`` ``.mcvd``
    - ``.obj`` ``.glb`` ``.dae`` ``.ms3d``
  * - 🧱 **Texture**
    - ``.ol``
    - ``.dds``
  * - 🖼️ **Image**
    - ``.mic``
    - ``.png``
  * - 📦 **Archive**
    - ``.texarr``
    - ``.zip``
  * - ⚙️ **Data**
    - ``NBT``\*
    - ``.json``

\* ``NBT`` refers to specific files (``itemnames.dat``, ``prefs``, ``sd0``, etc.)


.. important::

  | **Reverse conversion** (``standard`` → ``game``) **is not available.**
  | 📚 :doc:`See FAQ for details → <faq>`


.. seealso::

  📚 :doc:`Detailed formats support → <support>`


----------------------------------------
🚀 Quick Start
----------------------------------------

  **Three ways to get started:** download, install, or compile.

1. 💻 Download executable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Standalone ``scfile.exe`` available on `Releases page <https://github.com/onejeuu/sc-file/releases>`_
| *No Python required.*

**Usage:**

- 📥 **Drag & Drop**: drag file onto ``scfile.exe``
   `What is drag and drop? <DND_>`_
- 🖱️ **Open With**: set as default app for supported formats
   `How to set default app (Windows)? <DEFAPP_>`_
- 📟 **Command Line**: ``scfile.exe --help``
   | `What is command line interface? <CLI_>`_
   | *Example:* ``scfile.exe model.mcsb -F glb --skeleton``
   | *Options:* ``-F`` *picks model format,* ``--skeleton`` *extracts armature.*

2. 🐍 Install Python package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Install:**

.. code-block:: bash

  pip install sc-file


**Usage:**

- 📖 **Python library**: *See Library section*
- 📟 **CLI via package**: ``scfile --help``

3. 🔧 Compile from source
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

  from scfile import convert, formats, UserOptions

  # Simple conversion (auto detect format by file suffix)
  # User options to control parsing and export settings
  convert.auto("model.mcsb", options=UserOptions(parse_skeleton=True))

  # Advanced control (manual decoding and data inspection)
  # Context manager ensures proper resource cleanup
  with formats.mcsb.McsbDecoder("model.mcsb") as mcsb:
    # Access parsed scene data: meshes, bones
    scene = mcsb.decode().scene
    print(f"Model total vertices: {sum(m.count.vertices for m in scene.meshes)}")

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

| ``kommunist2021`` · ``Art3mLapa`` · ``n1kodim``
| ``IExploitableMan`` · ``Sarioga`` · ``Hazart``

Thanks to everyone who reported issues, shared findings, or contributed ideas.