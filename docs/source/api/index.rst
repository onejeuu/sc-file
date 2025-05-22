Library
==================================================

Choose appropriate API based on your needs:

* **For simple conversion** (recommended for most users):

  Use :mod:`scfile.convert` — high-level functions with automatic or specific format conversion.

  .. code-block:: python

    scfile.convert.auto("model.mcsa")
    scfile.convert.formats.ol_to_dds("texture.ol")

* **For advanced control** (e.g., custom pipelines):

  Use :mod:`scfile.formats` — low-level access to decoders/encoders.

  .. code-block:: python

    with McsaDecoder("model.mcsa") as mcsa:
      mcsa.to_obj().save("output.obj")

* **For data inspection/modification**:

  Use :mod:`scfile.core.context` & :mod:`scfile.structures` — access to parsed model data (meshes, textures, etc.).

.. toctree::
  :maxdepth: 3

  scfile
