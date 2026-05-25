🔧 Compile
==================================================

.. include:: _links.rst

.. important::
  These instructions are tailored for `astral-sh/uv <UV_>`_.


.. code-block:: bash
    :caption: Download source code

    git clone https://github.com/onejeuu/sc-file.git
    cd sc-file

.. code-block:: bash
    :caption: Compile without GUI

    uv run --group build scripts/build.py

.. code-block:: bash
    :caption: Compile with GUI

    uv run --group build --extra gui scripts/build.py

Executable ``scfile.exe`` will be created in ``sc-file/dist`` directory.
