sc-file
==================================================

.. include:: _links.rst

.. toctree::
  :maxdepth: 1

  usage
  faq
  formats
  compile

  api/index
  v/index


**scfile** is a utility and library for converting proprietary STALCRAFT asset formats to standard ones.

  This is an **unofficial** project and is **not affiliated** with EXBO.


----------------------------------------
✨ Supported Formats
----------------------------------------

.. list-table::
  :header-rows: 1

  * - Type
    - Game formats
    - →
    - Standard formats
  * - 🧊 **Model**
    - ``.mcsb`` ``.efkmodel``
    - →
    - ``.obj`` ``.glb`` ``.fbx``
  * - 🌀 **Animation**
    - | ``.mcvd`` + ``.mcsb``
      | ``.mcal`` + ``.mcsb``
    - →
    - ``.glb``
  * - 🧱 **Texture**
    - ``.ol``
    - →
    - ``.dds``
  * - 🖼️ **Image**
    - ``.mic``
    - →
    - ``.png``
  * - 🗃️ **TextureArray**
    - ``.texarr``
    - →
    - ``.zip``
  * - 🗺 **Region**
    - ``.mdat``
    - →
    - ``.mca``
  * - ⚙️ **NBT**
    - | ``itemnames.dat`` ``common``
      | ``prefs`` ``sd0-4``
    - →
    - ``.json``

:doc:`Detailed formats support → <formats>`


.. important::

  | **Reverse conversion** (``standard`` → ``game``) **is not available.**
  | :doc:`See FAQ for details → <faq>`


----------------------------------------
🚀 Usage
----------------------------------------

Download executable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download ``scfile.exe`` from the `Releases page <RELEASES_>`_.

**Usage:**

- **Graphical interface:** launch ``scfile.exe``.
- **Drag and drop:** drag files or folders onto ``scfile.exe`` in File Explorer.
- **Command line:** run ``scfile.exe --help`` for commands and options.

For example:

.. code-block:: console

  scfile.exe model.mcsb -F glb --skeleton

This exports the model and its armature to GLB. See the :doc:`usage guide <usage>` for batch conversion, animations, map regions, output layouts, and other options.


Install the Python package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

  pip install sc-file
  pip install "sc-file[gui]"  # extra graphical interface

The base package includes the library and CLI. The GUI is an optional extra.


Compile from source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See the :doc:`build guide <compile>` for development, contributions, and custom builds.


----------------------------------------
📖 Library
----------------------------------------

Install or update the package:

.. code-block:: console

  pip install sc-file -U


**Usage example:**

.. code-block:: python

  from scfile import convert, formats, Options

  # Detect the source format and convert it
  convert.auto("model.mcsb", options=Options(skeleton=True))

  # Use an explicit conversion and output path
  convert.mcsb_to_obj("model.mcsb", "output/model.obj")

  # Decode a known format and inspect its data
  with formats.McsbDecoder("model.mcsb") as mcsb:
      model = mcsb.decode()

  print([mesh.name for mesh in model.scene.meshes])
  print([bone.name for bone in model.scene.skeleton.bones])


:doc:`Complete library documentation → <api/index>`


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
