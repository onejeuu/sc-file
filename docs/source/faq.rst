❓ FAQ
==================================================

.. include:: _links.rst


----------------------------------------
📌 General
----------------------------------------

Q: Can files be encoded back into game formats?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

No. Reverse encoding is not available.

An open source encoder would let users alter client assets to easy.
It would lower the barrier to changes intended to gain an advantage.
It could also provoke stricter asset protection or repeated format changes, making legitimate extraction and research harder.
Public functionality therefore ends at decoding and export.


Q: Game update broke <Any Filename> decoding!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An update may introduce a new format version or a file variant unsupported by the current decoder.
Try the latest release. If the problem remains, `open an issue <ISSUES_>`_ and attach the file.


Q: Could using this program lead to a game ban?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The `License Agreement <EXBO_LICENSE_>`_ prohibits replacing or modifying game files except in `documented cases <EXBO_FILES_>`_.
Violating this restriction can lead to a ban. The agreement does not define a safe purpose or threshold for a particular replacement.

To avoid accidental replacement, work with copies and keep output outside the game directory.


----------------------------------------
📤 Output Formats
----------------------------------------

Q: What programs support ``.dds`` files?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Recommended viewers:
  - XnView_ (Universal)
  - WTV_ (Lightweight)


Q: How to convert ``.dds`` textures to ``.png``?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Convert DDS with ImageMagick_ or FFmpeg_.

.. code-block:: bash
  :caption: ImageMagick

  magick convert input.dds output.png

.. code-block:: bash
  :caption: FFmpeg

  ffmpeg -i input.dds output.png


Q: Why do models have weird or black textures?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In Blender, make sure texture node alpha mode is set to ``Channel Packed`` (`Screenshot <ALPHAMODE_>`_).


----------------------------------------
🛠 Troubleshooting
----------------------------------------

Q: Antivirus or SmartScreen blocks ``scfile.exe``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SmartScreen evaluates the reputation of a downloaded file and its publisher.
An unsigned new executable may therefore be shown as unrecognized. `Microsoft documents this behaviour <SMARTSCREEN_>`_.

VirusTotal aggregates independent engine results.
A detection from one engine is neither proof of malware nor a reason to ignore the warning.
Executables built with PyInstaller can trigger generic heuristic detections, as documented in the `PyInstaller issue tracker <PYINSTALLER_ISSUE_>`_.


Q: How to report a bug?
^^^^^^^^^^^^^^^^^^^^^^^

For a reproducible conversion failure, wrong output, or crash, `open an issue <ISSUES_>`_.

Please include:

- **Version and system**: sc-file version and operating system.
- **Exact action**: CLI command or GUI settings.
- **Expected and actual result**: include the complete error message.
- **Related file**: its path or an attachment when the problem concerns a file.

Questions and usage advice belong in `Telegram <TG_>`_.


----------------------------------------
❤️ Support
----------------------------------------

If this tool has been useful, you can support its development by `donation <DONATE_>`_.
