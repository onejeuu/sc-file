❓ FAQ
==================================================

.. include:: _links.rst


----------------------------------------
📌 General
----------------------------------------

Q: How to encode files back into game formats?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| **Reverse encoding is unsupported on purpose.**
| Even though it's possible to create this feature, making it public could cause problems.

1. **Cheating concerns**: Public reverse encoding would make creating hacks much easier, attracting unwanted attention and undermining this tool purpose.
2. **Formats changes risk**: If modifying game files becomes too easy, developers might start encrypting or complicating their assets, making them inaccessible for everyone.


Q: After game update ``%any_filename%`` no longer decodes!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Format structure may have been updated. Wait for program update. In case of large changes, it might take some time to adapt.


Q: Could using this program lead to game ban?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use at your own risk.

.. admonition:: Basic recommendations
  :class: important

  - You **MUST** close both game and launcher **BEFORE** interacting with any assets files.
  - You **MUST NOT** leave any files or modifications in game assets directory.
  - You **SHOULD** copy required files to separate directory **BEFORE** performing any manipulations.


----------------------------------------
📤 Output Formats
----------------------------------------

Q: What programs supports ``.dds`` viewing?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Any programs with full support for all `DirectDraw Surface <DDS_>`_ formats.

.. admonition:: Recommended Viewers
  :class: tip

  - `XnView <XNVIEW_>`_ (Universal)
  - `WTV <WTV_>`_ (Lightweight)
  - `RenderDoc <RENDERDOC_>`_ (Analysis)


Q: How to convert ``.dds`` textures to ``.png``?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Native support is not planned.

Convert ``.dds`` to ``.png`` using `ImageMagick <IMAGEMAGICK_>`_ or `FFmpeg <FFMPEG_>`_.

.. code-block:: bash
  :caption: ImageMagick

  magick convert input.dds output.png

.. code-block:: bash
  :caption: FFmpeg

  ffmpeg -i input.dds output.png


Q: Why do models have weird or black textures?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make sure texture node alpha mode is set to ``Channel Packed`` (`Screenshot <ALPHAMODE_>`_).

| Some models seem to have mixed-up suffixes in filenames.
| Make sure that the ``_diff`` texture is actually a Diffuse Map and the ``_spek`` texture is a Specular Map.
| :doc:`More about Suffix Conventions... <formats>`


----------------------------------------
🛠 Troubleshooting
----------------------------------------

Q: Antivirus or SmartScreen blocks ``scfile.exe``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The source code is open and anyone can inspect it at `GitHub <GITHUB_>`_.

| SmartScreen warns because the executable has **no digital signature**.
| Code signing certificates are not feasible for a free project.

| Antivirus detections on VirusTotal are **false positives**.
| Executable program is built with `PyInstaller <PYINSTALLER_>`_, a tool that packages Python scripts into standalone ``.exe``.
| Malware authors also use PyInstaller, so low-quality antivirus engines flag **any** PyInstaller executable.


Q: Something doesn't work as expected
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a file fails to convert, produces wrong output, or causes a crash, `open an issue <ISSUES_>`_.

Please include:

- **What happened**: error message, wrong output, etc.
- **What you expected**: correct output, different format, etc.
- **Which file (if any)**: attach file or describe path. Without it, bug cannot be reproduced.

| Reports without a file or clear description are hard to fix.
| The more details you provide, the faster is fix.
