📖 Library
==================================================

Choose appropriate API based on your needs:

* **For simple conversion** (recommended for most users):

  Use :mod:`scfile.convert` — high-level functions with automatic or specific format conversion.

  .. code-block:: python

    from scfile import convert

    convert.auto("model.mcsb") # Auto detect format by file suffix
    convert.formats.ol_to_dds("texture.ol") # Convert ol to dds
    convert.formats.mcsb_to_obj("model.mcsb") # Convert mcsb to obj

* **For advanced control** (e.g., custom pipelines):

  Use :mod:`scfile.formats` — low-level access to decoders/encoders.

  .. code-block:: python

    from scfile import formats

    # Decode mcsb model, convert to obj and save file
    with formats.mcsb.McsbDecoder("model.mcsb") as mcsb:
      mcsb.to_obj().save("output.obj")

* **For data inspection/modification**:

  Use :mod:`scfile.core.context` & :mod:`scfile.structures` — access to parsed model data (meshes, textures, etc.).

.. toctree::
  :maxdepth: 3

  scfile
