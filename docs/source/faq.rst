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
2. **Formats changes risk**: If modifying game files becomes too easy, developers might start encrypting or complicating their assets.

**My goal is to support research and creativity, not to create tools that could harm the game community.**

.. note::

  If you need assistance with in-game content creation tasks, you can `contact me directly <TG_>`_.


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

Native support is not planned for code simplicity.

| If needed, convert ``.dds`` to ``.png`` using `ImageMagick <IMAGEMAGICK_>`_.

.. code-block:: bash
  :caption: Command Example

  magick mogrify -format png *.dds


Q: Why model have weird/black textures?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make sure texture node alpha mode is set to ``Channel Packed`` (`Screenshot <ALPHAMODE_>`_).

| Some models seem to have mixed-up suffixes in filenames.
| Make sure that the ``_diff`` texture is actually a Diffuse Map and the ``_spek`` texture is a Specular Map.
| :doc:`More about Suffix Conventions... <formats>`


----------------------------------------
⛔ Unsupported Formats
----------------------------------------

Q: Why animations library (``.mcal``) unsupported?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This format is currently unusable due to its fragmented and technical nature.

| For example: character animations stored in ``pack.mcal``.
| But each has just few frames, totaling around **~5,000** entries.

| Unpacking is pointless, these are just broken-up animation fragments, not usable clips.
| Also, CLI can't handle them. They need paired model files, breaking current input logic.

*This might change in the future, but for now, there's no clear solution.*


Q: Why world map cache (``.mdat``) unsupported?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Structure resembles `minecraft chunk <MCA_>`_. But this format is too complex and possibly `AES Encrypted <AES_>`_.
| If you figure it out, feel free to contribute to `Pull Requests <https://github.com/onejeuu/sc-file/pulls>`_.


Q: Why json bundle (``.xeon``) unsupported?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This format is `AES Encrypted <AES_>`_. This encryption is unbreakable.

If you have information about key (password) for game assets, would be nice to know details `in DM <TG_>`_.
