❓ FAQ
==================================================

.. include:: _links.rst


----------------------------------------
📌 General
----------------------------------------

Q: Is it safe to use this program?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. Using this program to unpack and export assets is safe.

*Be careful when sharing this project on official game channels or communities,
as such tools may be considered undesirable and may be removed or moderated there.*


Q: Can I modify or replace game files?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Not recommended.

The `License Agreement <EXBO License_>`_ expressly prohibits modifying game files
except in `documented cases <EXBO Mods_>`_.
Violating this restriction may lead to ban.
There is no known safe threshold for a particular modification.
Avoid any changes that could provide in game advantages.


Q: Can files be encoded back into game formats?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

No. Reverse encoding is not available.

An open source encoder would let users alter client assets too easy.
It would lower the barrier to changes intended to gain an advantage.
It could also provoke stricter asset protection or repeated format changes,
making legitimate extraction and research harder.
Public functionality therefore ends at unidirectional export.


Q: Game update broke <Any Filename> decoding!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An update may introduce a new format version or a file variant unsupported by the current decoder.
Try the latest release. If the problem remains, `open an issue <Issues_>`_ and attach the file.
In case of large changes, it might take some time to adapt.


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

Use ImageMagick_ or FFmpeg_.

.. code-block:: bash
  :caption: ImageMagick

  magick convert input.dds output.png

.. code-block:: bash
  :caption: FFmpeg

  ffmpeg -i input.dds output.png


Q: Why do models have weird or black textures?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In Blender, make sure node alpha mode is set to ``Channel Packed`` (`Screenshot <Alpha Mode_>`_).


----------------------------------------
🛠 Troubleshooting
----------------------------------------

Q: Antivirus or SmartScreen blocks ``scfile.exe``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SmartScreen evaluates the reputation of a downloaded file and its publisher.
An unsigned new executable may therefore be shown as unrecognized.
`Microsoft documents this behaviour <SmartScreen_>`_.

VirusTotal aggregates independent engine results.
**A detection from one engine is neither proof of malware nor a reason to ignore the warning.**
Executables built with PyInstaller_ can trigger generic heuristic detections,
as documented in the `PyInstaller issue tracker <PyInstaller Issue_>`_.


Q: How to report a bug?
^^^^^^^^^^^^^^^^^^^^^^^

For a reproducible conversion failure, wrong output, or crash, `open an issue <Issues_>`_.

Please include:

- **Version and system**: sc-file version and operating system.
- **Exact action**: CLI command or GUI settings.
- **Expected and actual result**: include the complete error message.
- **File**: its path or an attachment when the problem concerns a file.

Questions and usage advice belong in `Telegram <TG_>`_.


----------------------------------------
❤️ Support
----------------------------------------

If this tool has been useful, you can support its development by donation: NOWPayments_, CloudTips_.
