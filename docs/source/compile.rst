🔧 Compile
==================================================

.. include:: _links.rst

.. important::
  These instructions are tailored for `astral-sh/uv <UV_>`_.


.. code-block:: bash
    :caption: Download source code

    git clone https://github.com/onejeuu/sc-file.git
    cd sc-file

Portable executable
----------------------------------------

.. code-block:: bash
    :caption: Compile without GUI

    uv run --group build scripts/build.py

.. code-block:: bash
    :caption: Compile with GUI

    uv run --group build --extra gui scripts/build.py

Creates ``dist/scfile.exe`` on Windows or ``dist/scfile`` on Linux.

Windows setup
----------------------------------------

Install `Inno Setup`_. Restart the terminal after installation.

.. code-block:: bash

    uv run --group build --extra gui scripts/build.py --setup

Creates ``dist/scfile_setup.exe``.
