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

1. **Cheating concerns**: Public reverse encoding would make creating hacks much easier, attracting unwanted attention and undermining the tool's purpose.
2. **Format change risk**: If modifying game files becomes too easy, developers might start encrypting or complicating their assets, making them inaccessible for everyone.


Q: After a game update ``%any_filename%`` no longer decodes!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Format structure may have been updated. Wait for program update. In case of large changes, it might take some time to adapt.


Q: Could using this program lead to a game ban?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use at your own risk.

.. admonition:: Basic recommendations
  :class: important

  - You **MUST** close both game and launcher **BEFORE** interacting with any asset files.
  - You **MUST NOT** leave any files or modifications in the game asset directory.
  - You **SHOULD** copy required files to a separate directory **BEFORE** working with them.


----------------------------------------
📤 Output Formats
----------------------------------------

Q: What programs support ``.dds`` files?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Any program with full support for all `DirectDraw Surface <DDS_>`_ formats.

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

In Blender, make sure texture node alpha mode is set to ``Channel Packed`` (`Screenshot <ALPHAMODE_>`_).

| Some models seem to have mixed-up suffixes in filenames.
| Make sure that the ``_diff`` texture is actually a Diffuse Map and the ``_spek`` texture is a Specular Map.
| :doc:`More about Suffix Conventions... <formats>`


----------------------------------------
🛠 Troubleshooting
----------------------------------------

Q: Antivirus or SmartScreen blocks ``scfile.exe``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The source code is open and anyone can inspect it on `GitHub <GITHUB_>`_.

| SmartScreen warns because the executable has **no digital signature**.
| Code signing certificates are not feasible for a free project.

| Antivirus detections on VirusTotal are **false positives**.
| Executable is built with `PyInstaller <PYINSTALLER_>`_, a tool that packages Python scripts into standalone ``.exe``.
| Malware authors also use PyInstaller, so some low-quality antivirus engines flag unsigned PyInstaller executables.


Q: Something doesn't work as expected
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a file fails to convert, produces wrong output, or causes a crash, `open an issue <ISSUES_>`_.

Please include:

- **What happened**: error message, wrong output, etc.
- **What you expected**: correct output, different format, etc.
- **Which file (if any)**: provide its path or attach it.

| Reports without a file path or clear description are hard to fix.
| More detail usually means a faster fix.
