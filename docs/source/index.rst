Index
==================================================

.. toctree::
  :maxdepth: 1

  usage
  faq
  formats
  support
  compile

  api/index


----------------------------------------
Overview
----------------------------------------

**scfile** is a utility and library for parsing and converting stalcraft assets (such as models and textures), into standard formats.

| 🗂️ Supported game formats: ``.mcsb``, ``.mcsa``, ``.mcvd``, ``.ol``, ``.mic``, ``.texarr``.
| :doc:`More about Game Formats... <formats>`

| 💻 Executable utility ``scfile.exe`` can be downloaded from `Releases page <https://github.com/onejeuu/sc-file/releases>`_ or :doc:`compiled from source <compile>`.
| :doc:`More about Usage... <usage>`

| ❓ **Why reverse encoding into game formats is unsupported?**
| And other common questions are answered on :doc:`FAQ page <faq>`.

.. list-table:: 🛠️ Supported Formats
  :header-rows: 1

  * - Type
    - Source
    - Output
  * - 🧊 Model
    - ``.mcsb``, ``.mcsa``, ``.mcvd``
    - ``.obj``, ``.glb``, ``.dae``, ``.ms3d``
  * - 🧱 Texture
    - ``.ol``
    - ``.dds``
  * - 🖼️ Image
    - ``.mic``
    - ``.png``
  * - 📦 Archive
    - ``.texarr``
    - ``.zip``

:doc:`More about Formats Support... <support>`


----------------------------------------
🚀 Quick Start
----------------------------------------

.. code-block:: bash
  :caption: Command example

  scfile.exe model.mcsb -F dae --skeleton

:doc:`More about Usage... <usage>`


----------------------------------------
📖 Library
----------------------------------------

To install library for coding, use following command:

.. code-block:: bash

  pip install sc-file -U

.. code-block:: python
  :caption: Simple usage example

  from scfile import convert
  from scfile.core.context import UserOptions

  convert.mcsb_to_obj(source="path/to/model.mcsb", options=UserOptions(parse_skeleton=True))

:doc:`More details about Library... <api/index>`


----------------------------------------
🤝 Acknowledgments
----------------------------------------

- ``kommunist2021`` – file structure research.
- ``Art3mLapa`` – advice, bug reports.
- ``n1kodim`` – advice, contribution.
- ``IExploitableMan`` – contribution.
- ``Sarioga`` – feedback, bug reports.
- ``Hazart`` – bug reports.
