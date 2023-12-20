SC FILES
==========================

Library and Utility for converting encrypted ``stalcraft`` game files, such as models and textures into well-known formats.

You can use compiled cli utility from `Releases <https://github.com/onejeuu/sc-file/releases>`_ page.


⚠️ Disclaimer
-------------

**Do not use game assets folder directly.**

You can get banned for any changes in game client.


📁 Formats
----------

.. list-table::
   :widths: 20 20 20

   * - Type
     - Source format
     - Output format
   * - Model
     - .mcsa
     - .obj
   * - Texture
     - .mic
     - .png
   * - Texture
     - .ol
     - .dds


💻 CLI Utility
--------------

Usage
~~~~~

You can drag and drop one or multiple files to ``scfile.exe``.

From bash:

.. code:: bash

    scfile [OPTIONS] [FILES]...

Arguments
~~~~~~~~~

- ``FILES``: **List of file paths to be converted**. Multiple files should be separated by **spaces**. Accepts both full and relative paths. **Does not accept directory**.

Options
~~~~~~~

- ``-O``, ``--output``: **One path to output file or directory**. Can be specified multiple times for different output files or directories. If not specified, file will be saved in the same directory with a new suffix. You can specify multiple ``FILES`` and a single ``--output`` directory.

Examples
~~~~~~~~

1. Convert a single file:

    .. code:: bash

        scfile file.mcsa

    Will be saved in the same directory with a new suffix.

2. Convert a single file with a specified path or name:

    .. code:: bash

        scfile file.mcsa --output path/to/file.obj

3. Convert multiple files to a specified directory:

    .. code:: bash

        scfile file1.mcsa file2.mcsa --output path/to/folder

4. Convert multiple files with explicitly specified output files:

    .. code:: bash

        scfile file1.mcsa file2.mcsa -O 1.obj -O 2.obj

    If the count of ``FILES`` and ``-O`` is different, as many files as possible will be converted.

5. Convert all ``.mcsa`` files in the current directory:

    .. code:: bash

        scfile *.mcsa

    In this case, ``-O`` accepts only a directory. Subfolders are not included.

6. Convert all ``.mcsa`` files with subfolders to a specified directory:

    .. code:: bash

        scfile **/*.mcsa -O path/to/folder

    In this case, ``-O`` accepts only a directory. With ``-O`` specified, the folder structure is not duplicated.


📚 Library
----------

Install
~~~~~~~

Pip
~~~

.. code:: bash

    pip install sc-file -U

Manual
~~~~~~

.. code:: bash

    git clone git@github.com:onejeuu/sc-file.git

.. code:: bash

    cd sc-file

.. code:: bash

    poetry install

Usage
~~~~~

Simple
^^^^^^

.. code:: python

    from scfile import convert

    # Output path is optional.
    # Defaults to source path with new suffix.
    convert.mcsa_to_obj("path/to/file.mcsa", "path/to/file.obj")
    convert.mic_to_png("path/to/file.mic", "path/to/file.png")
    convert.ol_to_dds("path/to/file.ol", "path/to/file.dds")

Advanced
^^^^^^^^

.. code:: python

    from scfile import McsaFile

    with McsaFile("path/to/file.mcsa") as mcsa:
        obj: bytes = mcsa.to_obj()

    with open("path/to/file.obj", "wb") as fp:
        fp.write(obj)

🛠️ Build
--------

You will need poetry to do compilation. Install it `here <https://python-poetry.org>`_.

Before proceeding, it's recommended to create virtual environment:

.. code:: bash

    poetry shell

Then install dependencies:

.. code:: bash

    poetry install

And run script to compile:

.. code:: bash

    poetry run build

Executable file will be created in ``/dist`` directory within your project folder.
