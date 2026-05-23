📖 Library
==============

The Reference API is divided into execution layers depending on the required control granularity.

.. toctree::
  :maxdepth: 2

  usage/index


High-Level Conversion (:mod:`scfile.convert`)
---------------------------------------------------------------
Provides simplified, single function access for automated format conversion.

.. code-block:: python

  from scfile import convert

  # Automated format detection via file extension
  convert.auto("model.mcsb")
  convert.auto("model.mcsb", output="path/to/output/dir")

  # Explicit format pair conversion
  convert.formats.mcsb_to_obj("model.mcsb", output="output.obj")


Advanced Pipelines (:mod:`scfile.formats`)
---------------------------------------------------------------
Provides explicit control over decoding and encoding lifecycle using context managers.

.. code-block:: python

  from scfile.formats.mcsb import McsbDecoder

  with McsbDecoder("model.mcsb") as mcsb:
    mcsb.to_obj().save("output.obj")


Data Inspection (:mod:`scfile.structures`)
---------------------------------------------------------------
Provides direct access to parsed structures and underlying data containers before serialization.

.. code-block:: python

  from scfile.formats.mcsb import McsbDecoder
  from scfile import Options

  options = Options(skeleton=True)

  with McsbDecoder("model.mcsb", options=options) as mcsb:
    content = mcsb.decode()

    print(f"Version: {content.version}")
    print(f"Polygons: {content.scene.total_polygons}")
    print(f"Bones: {[bone.name for bone in content.scene.skeleton.bones]}")


API Reference
---------------------------------------------------------------

.. toctree::
  :maxdepth: 3

  scfile
