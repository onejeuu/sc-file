📖 Library
==================================================

The API is organized by level of control.

.. toctree::
  :maxdepth: 2

  usage/index


High-Level Conversion
----------------------------------------

Use :mod:`scfile.convert` for automatic format detection and named conversion functions.

.. code-block:: python

  from scfile import convert

  convert.auto("model.mcsb")
  convert.auto("model.mcsb", output="path/to/output/dir")

  convert.formats.mcsb_to_obj("model.mcsb", output="output.obj")


Advanced Pipelines
----------------------------------------

Use decoders and encoders from :mod:`scfile.formats` for control over their lifecycle.

.. code-block:: python

  from scfile.formats import McsbDecoder

  with McsbDecoder("model.mcsb") as mcsb:
    mcsb.as_obj().save("output.obj")


Data Inspection
----------------------------------------

Use :mod:`scfile.structures` to inspect decoded content before encoding it.

.. code-block:: python

  from scfile import Options
  from scfile.formats.mcsb import McsbDecoder

  options = Options(skeleton=True)

  with McsbDecoder("model.mcsb", options=options) as mcsb:
    content = mcsb.decode()

    print(f"Version: {content.version}")
    print(f"Polygons: {content.scene.total_polygons}")
    print(f"Bones: {[bone.name for bone in content.scene.skeleton.bones]}")


API Reference
----------------------------------------

.. toctree::
  :maxdepth: 3

  scfile
