Frequently Asked Questions
==================================================


----------------------------------------
General
----------------------------------------

Q: How to encode files back into game formats?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Answer:** Reverse encoding is intentionally unsupported. While this functionality is technically possible, releasing it publicly could lead to unwanted consequences.

1. **Risk of format changes**: If an easy way to modify game files becomes available, it might encourage game developers to complicate or even encrypt game assets.

2. **Potential cheating issues**: An open reverse encoding feature could significantly simplify creating hacks. This might attract negative attention from game developers and lead to the tool being seen as a cheat making utility, which I aim to avoid.

My goal is to support research and creativity, not create tools that could harm the game community. If you need help with small tasks in game content creation, you can `contact me directly <https://onejeuu.t.me>`_.


Q: After game update ``%any_filename%`` no longer decodes!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Answer:** Format structure may have been updated. Wait for program update. In case of large changes, it might take some time to adapt.


Q: Could using this program lead to game ban?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Answer:** Use at your own risk.

**Some basic recommendations:**
  - You **MUST** close both game and launcher before interacting with **ANY** assets files.
  - You **MUST NOT** leave any files or modifications in game assets directory.
  - You **SHOULD** copy required files to separate directory **BEFORE** performing any manipulations.


----------------------------------------
Models & Textures
----------------------------------------

Q: What programs can I use to view ``.dds`` textures and their thumbnails?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Answer:** Any programs with full support for all ``.dds`` (`DirectDraw Surface <https://en.wikipedia.org/wiki/DirectDraw_Surface>`_) formats.

**Recommended Viewers:**
  - `XnView <https://xnview.com>`_ (Versatile)
  - `WTV <https://www.softpedia.com/get/Multimedia/Graphic/Graphic-Viewers/WTV.shtml>`_ (Lightweight)
  - `RenderDoc <https://renderdoc.org/builds>`_ (Analysis)


Q: Is it possible to convert ``.dds`` textures to ``.png``?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Answer:** Yes, but native support is not planned for code simplicity.

| If needed, convert ``.dds`` to ``.png`` using `ImageMagick <https://imagemagick.org>`_.
| Command example:

.. code-block:: bash

  magick mogrify -format png *.dds


Q: Why model have weird/black textures?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Answer:** Make sure texture node alpha mode is set to ``Channel Packed`` (`Screenshot <https://i.ibb.co/mCsHk6R4/alphapvp.png>`_).

| Some models seem to have mixed-up suffixes in filenames.
| Make sure that the ``_diff`` texture is actually a Diffuse Map and the ``_spek`` texture is a Specular Map.
| :doc:`More about Suffix Conventions... <formats>`


----------------------------------------
Other Features
----------------------------------------

Q: How to get character animations (``.mcal``)?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Answer:** Right now, it's not possible.

| Character animations are stored in ``pack.mcal``
| But they are technical, each has just few frames, totaling around **~5,000** entries.

| Unpacking is pointless, these are just broken-up animation fragments, not usable clips.
| Also, CLI can't handle them. They need paired model files, breaking current input logic.

*This might change in the future, but for now, there's no clear solution.*


Q: How to open other file types (e.g. ``.xeon``)?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Answer:** These files are encrypted using `AES <https://en.wikipedia.org/wiki/Advanced_Encryption_Standard>`_ and cannot be decrypted without the key.

If anyone has information about key for assets, it would be nice to know details in `DM <https://onejeuu.t.me>`_.


Q: Is it possible to get game map as a model?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Answer:** Theoretically, yes, but this is currently not supported.

If anyone wants to implement a map cache decoder, feel free to contribute to `Pull Requests <https://github.com/onejeuu/sc-file/pulls>`_.
