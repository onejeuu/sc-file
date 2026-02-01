🔧 Compile
==================================================

.. include:: _links.rst

.. important::
  This instructions are tailored for `astral-sh/uv <UV_>`_.


1. Download project

  .. code-block:: console

    git clone https://github.com/onejeuu/sc-file.git


  .. code-block:: console

    cd sc-file

2. Recommended to create virtual environment

  .. code-block:: console

    uv venv; .venv\Scripts\activate

3. Install dependencies

  .. code-block:: console

    uv sync

4. Run the build script

  .. code-block:: console

    uv run scripts/build.py

  Executable file ``scfile.exe`` will be created in ``/dist`` directory.
